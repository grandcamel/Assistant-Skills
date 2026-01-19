/**
 * Invite validation service.
 */

const config = require('../config');
const { getTracer, invitesValidatedCounter } = require('../config/metrics');
const state = require('./state');

// Invite brute-force protection state
const inviteRateLimits = new Map(); // ip -> { count, resetAt }

/**
 * Check if invite validation is allowed from this IP (brute-force protection).
 * @param {string} ip - Client IP address
 * @returns {Object} { allowed: boolean, retryAfter?: number }
 */
function checkInviteRateLimit(ip) {
  const now = Date.now();
  const record = inviteRateLimits.get(ip);

  // Clean up expired entry
  if (record && now > record.resetAt) {
    inviteRateLimits.delete(ip);
  }

  const current = inviteRateLimits.get(ip);
  if (!current) {
    return { allowed: true };
  }

  if (current.count >= config.INVITE_RATE_LIMIT_MAX_ATTEMPTS) {
    const retryAfter = Math.ceil((current.resetAt - now) / 1000);
    return { allowed: false, retryAfter };
  }

  return { allowed: true };
}

/**
 * Record a failed invite attempt for this IP.
 * @param {string} ip - Client IP address
 */
function recordFailedInviteAttempt(ip) {
  const now = Date.now();
  const current = inviteRateLimits.get(ip);

  if (!current || now > current.resetAt) {
    inviteRateLimits.set(ip, { count: 1, resetAt: now + config.INVITE_RATE_LIMIT_WINDOW_MS });
  } else {
    current.count++;
  }
}

/**
 * Validate an invite token.
 * @param {Object} redis - Redis client
 * @param {string} token - Invite token
 * @param {string|null} clientIp - Client IP address
 * @returns {Promise<Object>} Validation result
 */
async function validateInvite(redis, token, clientIp = null) {
  const tracer = getTracer();
  const span = tracer?.startSpan('invite.validate', {
    attributes: { 'invite.token_prefix': token?.slice(0, 8) || 'none' }
  });

  try {
    // Token must be 4-64 chars, URL-safe characters only
    if (!token || !/^[A-Za-z0-9_-]{4,64}$/.test(token)) {
      invitesValidatedCounter?.add(1, { status: 'invalid' });
      span?.setAttribute('invite.status', 'invalid');
      return {
        valid: false,
        reason: 'invalid',
        message: 'This invite link is malformed or invalid.'
      };
    }

    const inviteKey = `invite:${token}`;
    const inviteJson = await redis.get(inviteKey);

    if (!inviteJson) {
      invitesValidatedCounter?.add(1, { status: 'not_found' });
      span?.setAttribute('invite.status', 'not_found');
      return {
        valid: false,
        reason: 'not_found',
        message: 'This invite link does not exist. Please check the URL or request a new invite.'
      };
    }

    const invite = JSON.parse(inviteJson);

    // Check if revoked
    if (invite.status === 'revoked') {
      invitesValidatedCounter?.add(1, { status: 'revoked' });
      span?.setAttribute('invite.status', 'revoked');
      return {
        valid: false,
        reason: 'revoked',
        message: 'This invite link has been revoked by an administrator.'
      };
    }

    // Check if already used
    if (invite.status === 'used' || (invite.useCount >= invite.maxUses)) {
      const activeSession = state.getActiveSession();

      // Allow rejoin if there's an active session from the same IP using this invite
      if (clientIp && activeSession && activeSession.inviteToken === token && activeSession.ip === clientIp) {
        console.log(`Allowing rejoin for used invite ${token.slice(0, 8)}... from same IP ${clientIp} (awaitingReconnect: ${activeSession.awaitingReconnect || false})`);
        invitesValidatedCounter?.add(1, { status: 'rejoin' });
        span?.setAttribute('invite.status', 'rejoin');
        return { valid: true, data: invite, rejoin: true };
      }

      // Also allow if there's a pending session token from the same IP
      for (const [, pending] of state.pendingSessionTokens) {
        if (pending.inviteToken === token && pending.ip === clientIp) {
          console.log(`Allowing rejoin for pending invite ${token.slice(0, 8)}... from same IP ${clientIp}`);
          invitesValidatedCounter?.add(1, { status: 'rejoin' });
          span?.setAttribute('invite.status', 'rejoin');
          return { valid: true, data: invite, rejoin: true };
        }
      }

      invitesValidatedCounter?.add(1, { status: 'used' });
      span?.setAttribute('invite.status', 'used');
      return {
        valid: false,
        reason: 'used',
        message: 'This invite link has already been used. Each invite can only be used once.'
      };
    }

    // Check expiration
    if (new Date(invite.expiresAt) < new Date()) {
      // Update status in Redis
      invite.status = 'expired';
      const ttl = await redis.ttl(inviteKey);
      await redis.set(inviteKey, JSON.stringify(invite), 'EX', ttl > 0 ? ttl : 86400);
      invitesValidatedCounter?.add(1, { status: 'expired' });
      span?.setAttribute('invite.status', 'expired');
      return {
        valid: false,
        reason: 'expired',
        message: 'This invite link has expired. Please request a new invite.'
      };
    }

    invitesValidatedCounter?.add(1, { status: 'valid' });
    span?.setAttribute('invite.status', 'valid');
    return { valid: true, data: invite };
  } finally {
    span?.end();
  }
}

/**
 * Record invite usage after session ends.
 * @param {Object} redis - Redis client
 * @param {Object} session - Session object
 * @param {Date} endedAt - Session end time
 * @param {string} endReason - Reason for session end
 * @param {number} auditRetentionDays - Days to retain audit data
 */
async function recordInviteUsage(redis, session, endedAt, endReason, auditRetentionDays) {
  const inviteKey = `invite:${session.inviteToken}`;

  try {
    const inviteJson = await redis.get(inviteKey);
    if (!inviteJson) {
      console.log(`Invite ${session.inviteToken} not found for usage recording`);
      return;
    }

    const invite = JSON.parse(inviteJson);

    // Add session record
    if (!invite.sessions) invite.sessions = [];
    invite.sessions.push({
      sessionId: session.sessionId,
      clientId: session.clientId,
      startedAt: session.startedAt.toISOString(),
      endedAt: endedAt.toISOString(),
      endReason: endReason,
      queueWaitMs: session.queueWaitMs,
      ip: session.ip,
      userAgent: session.userAgent,
      errors: session.errors || []
    });

    // Update usage tracking
    invite.useCount = (invite.useCount || 0) + 1;
    if (invite.useCount >= invite.maxUses) {
      invite.status = 'used';
    }

    // Save with extended TTL (audit retention after expiration)
    const expiresAtMs = new Date(invite.expiresAt).getTime();
    const auditRetentionMs = auditRetentionDays * 24 * 60 * 60 * 1000;
    const ttlSeconds = Math.max(
      Math.floor((expiresAtMs - Date.now() + auditRetentionMs) / 1000),
      86400  // At least 1 day
    );

    await redis.set(inviteKey, JSON.stringify(invite), 'EX', ttlSeconds);
    console.log(`Recorded usage for invite ${session.inviteToken.slice(0, 8)}..., status: ${invite.status}`);

  } catch (err) {
    console.error('Error recording invite usage:', err.message);
  }
}

/**
 * Clean up expired rate limit entries.
 */
function cleanupRateLimits() {
  const now = Date.now();
  for (const [ip, record] of inviteRateLimits.entries()) {
    if (now > record.resetAt) {
      inviteRateLimits.delete(ip);
    }
  }
}

module.exports = {
  checkInviteRateLimit,
  recordFailedInviteAttempt,
  validateInvite,
  recordInviteUsage,
  cleanupRateLimits
};
