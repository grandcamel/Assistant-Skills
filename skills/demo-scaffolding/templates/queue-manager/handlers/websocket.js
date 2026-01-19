/**
 * WebSocket connection handlers.
 */

const { v4: uuidv4 } = require('uuid');
const config = require('../config');
const state = require('../services/state');
const { joinQueue, leaveQueue, broadcastQueueUpdate, processQueue } = require('../services/queue');
const { endSession } = require('../services/session');

// Rate limiting state
const connectionRateLimits = new Map(); // ip -> { count, resetAt }

/**
 * Check if a connection from this IP is allowed (rate limiting).
 * @param {string} ip - Client IP address
 * @returns {Object} { allowed: boolean, retryAfter?: number }
 */
function checkConnectionRateLimit(ip) {
  const now = Date.now();
  const record = connectionRateLimits.get(ip);

  // Clean up expired entry
  if (record && now > record.resetAt) {
    connectionRateLimits.delete(ip);
  }

  // Cleanup old entries periodically
  if (connectionRateLimits.size > 1000) {
    for (const [key, value] of connectionRateLimits) {
      if (value.resetAt < now) connectionRateLimits.delete(key);
    }
  }

  const current = connectionRateLimits.get(ip);
  if (!current) {
    connectionRateLimits.set(ip, { count: 1, resetAt: now + config.RATE_LIMIT_WINDOW_MS });
    return { allowed: true };
  }

  if (current.count >= config.RATE_LIMIT_MAX_CONNECTIONS) {
    const retryAfter = Math.ceil((current.resetAt - now) / 1000);
    return { allowed: false, retryAfter };
  }

  current.count++;
  return { allowed: true };
}

/**
 * Clean up expired rate limit entries.
 */
function cleanupRateLimits() {
  const now = Date.now();
  for (const [ip, record] of connectionRateLimits.entries()) {
    if (now > record.resetAt) {
      connectionRateLimits.delete(ip);
    }
  }
}

/**
 * Set up WebSocket handlers.
 * @param {WebSocketServer} wss - WebSocket server
 * @param {Object} redis - Redis client
 */
function setup(wss, redis) {
  wss.on('connection', (ws, req) => {
    const clientIp = req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.socket.remoteAddress;
    const userAgent = req.headers['user-agent'] || 'unknown';

    // Check rate limit before accepting connection
    const rateLimit = checkConnectionRateLimit(clientIp);
    if (!rateLimit.allowed) {
      console.log(`Rate limit exceeded for ${clientIp}, rejecting connection`);
      ws.close(1008, `Rate limit exceeded. Retry after ${rateLimit.retryAfter} seconds.`);
      return;
    }

    // Validate WebSocket origin to prevent CSRF attacks
    const origin = req.headers.origin;
    if (origin && !config.ALLOWED_ORIGINS.includes(origin)) {
      console.log(`WebSocket connection rejected: invalid origin ${origin}`);
      ws.close(1008, 'Origin not allowed');
      return;
    }

    const clientId = uuidv4();

    state.clients.set(ws, {
      id: clientId,
      state: 'connected',
      joinedAt: null,
      ip: clientIp,
      userAgent: userAgent,
      inviteToken: null
    });

    console.log(`Client connected: ${clientId} from ${clientIp}`);

    ws.on('message', async (data) => {
      try {
        const message = JSON.parse(data);
        console.log("Received message:", message);
        await handleMessage(redis, ws, message);
      } catch (err) {
        console.error('Error handling message:', err.message);
        sendError(ws, 'Invalid message format');
      }
    });

    ws.on('close', () => {
      handleDisconnect(redis, ws);
    });

    ws.on('error', (err) => {
      console.error(`WebSocket error for ${clientId}:`, err.message);
    });

    // Send initial status
    sendStatus(ws);
  });
}

async function handleMessage(redis, ws, message) {
  const client = state.clients.get(ws);
  if (!client) return;

  const processQueueFn = () => processQueue(redis);

  switch (message.type) {
    case 'join_queue':
      await joinQueue(redis, ws, client, message.inviteToken, processQueueFn);
      break;

    case 'leave_queue':
      leaveQueue(ws, client);
      break;

    case 'heartbeat':
      ws.send(JSON.stringify({ type: 'heartbeat_ack' }));
      break;

    default:
      sendError(ws, `Unknown message type: ${message.type}`);
  }
}

function handleDisconnect(redis, ws) {
  const client = state.clients.get(ws);
  if (!client) return;

  console.log(`Client disconnected: ${client.id}`);

  const activeSession = state.getActiveSession();

  // Clean up pending session token (but keep it for grace period if in active session)
  if (client.pendingSessionToken && !(activeSession && activeSession.clientId === client.id)) {
    state.pendingSessionTokens.delete(client.pendingSessionToken);
  }

  // Remove from queue if waiting
  const queueIndex = state.queue.indexOf(client.id);
  if (queueIndex !== -1) {
    state.queue.splice(queueIndex, 1);
    broadcastQueueUpdate();
  }

  // End session with grace period if active (allows page refresh)
  if (activeSession && activeSession.clientId === client.id) {
    console.log(`Starting ${config.DISCONNECT_GRACE_MS/1000}s grace period for session ${activeSession.sessionId}`);

    // Store info needed for reconnection
    activeSession.disconnectedAt = new Date();
    activeSession.awaitingReconnect = true;

    // Clear any existing grace timeout
    state.clearDisconnectGraceTimeout();

    // Set grace period - session ends if no reconnect within timeout
    const graceTimeout = setTimeout(() => {
      const currentSession = state.getActiveSession();
      if (currentSession && currentSession.awaitingReconnect) {
        console.log('Grace period expired, ending session');
        endSession(redis, 'disconnected', () => processQueue(redis));
      }
      state.setDisconnectGraceTimeout(null);
    }, config.DISCONNECT_GRACE_MS);

    state.setDisconnectGraceTimeout(graceTimeout);
  }

  state.clients.delete(ws);
}

function sendStatus(ws) {
  ws.send(JSON.stringify({
    type: 'status',
    queue_size: state.queue.length,
    session_active: state.getActiveSession() !== null
  }));
}

function sendError(ws, message) {
  ws.send(JSON.stringify({ type: 'error', message }));
}

module.exports = { setup, cleanupRateLimits };
