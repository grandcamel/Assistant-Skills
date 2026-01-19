#!/usr/bin/env node
/**
 * Invite CLI Tool
 *
 * Generate and manage demo invite URLs with expiration.
 *
 * Usage:
 *   node invite-cli.js generate --expires 48h
 *   node invite-cli.js generate --expires 7d --label "Workshop"
 *   node invite-cli.js generate --expires 7d --token "VIP-JOHN" --label "VIP John"
 *   node invite-cli.js list [--status pending|used|expired|revoked]
 *   node invite-cli.js info <token>
 *   node invite-cli.js revoke <token>
 */

const crypto = require('crypto');
const Redis = require('ioredis');

// Configuration
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const BASE_URL = process.env.BASE_URL || 'http://localhost:8080';
const DEFAULT_EXPIRES = '48h';
const AUDIT_RETENTION_DAYS = 30;

const redis = new Redis(REDIS_URL);

// =============================================================================
// Duration Parsing
// =============================================================================

function parseDuration(duration) {
  const match = duration.match(/^(\d+)(m|h|d|w)$/);
  if (!match) {
    throw new Error(`Invalid duration format: ${duration}. Use: 30m, 48h, 7d, 2w`);
  }

  const value = parseInt(match[1], 10);
  const unit = match[2];

  const multipliers = {
    m: 60 * 1000,           // minutes
    h: 60 * 60 * 1000,      // hours
    d: 24 * 60 * 60 * 1000, // days
    w: 7 * 24 * 60 * 60 * 1000  // weeks
  };

  return value * multipliers[unit];
}

function formatDuration(ms) {
  const hours = Math.floor(ms / (60 * 60 * 1000));
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days}d`;
}

// =============================================================================
// Token Generation
// =============================================================================

function generateToken() {
  return crypto.randomBytes(12).toString('base64url');
}

function validateCustomToken(token) {
  // Must be 4-64 chars, URL-safe characters only
  if (!/^[A-Za-z0-9_-]{4,64}$/.test(token)) {
    throw new Error('Custom token must be 4-64 characters, using only A-Z, a-z, 0-9, dash, and underscore');
  }
  return token;
}

function validateLabel(label) {
  if (!label) return null;
  // Limit length to prevent storage exhaustion and log injection
  if (label.length > 100) {
    throw new Error('Label must be 100 characters or less');
  }
  // Sanitize: remove control characters and normalize whitespace
  // eslint-disable-next-line no-control-regex
  return label.replace(/[\x00-\x1f\x7f]/g, '').trim();
}

// =============================================================================
// Commands
// =============================================================================

async function generate(options) {
  // Use custom token if provided, otherwise generate random one
  const token = options.token ? validateCustomToken(options.token) : generateToken();

  // Validate and sanitize label
  const label = validateLabel(options.label);

  // Check if token already exists
  const existing = await redis.get(`invite:${token}`);
  if (existing) {
    console.error(`\nError: Token "${token}" already exists. Use a different token or revoke the existing one.\n`);
    process.exit(1);
  }

  const now = new Date();
  const expiresMs = parseDuration(options.expires || DEFAULT_EXPIRES);
  const expiresAt = new Date(now.getTime() + expiresMs);

  const invite = {
    token,
    createdAt: now.toISOString(),
    expiresAt: expiresAt.toISOString(),
    status: 'pending',
    maxUses: 1,
    useCount: 0,
    label: label,
    createdBy: 'cli',
    sessions: []
  };

  // Set TTL to expiration + audit retention period
  const ttlSeconds = Math.floor(expiresMs / 1000) + (AUDIT_RETENTION_DAYS * 24 * 60 * 60);

  await redis.set(`invite:${token}`, JSON.stringify(invite), 'EX', ttlSeconds);

  const inviteUrl = `${BASE_URL}/${token}`;

  console.log('\nInvite created successfully!\n');
  console.log(`Token:   ${token}`);
  console.log(`Expires: ${expiresAt.toISOString()} (${formatDuration(expiresMs)})`);
  if (options.label) {
    console.log(`Label:   ${options.label}`);
  }
  console.log(`\nInvite URL:\n${inviteUrl}\n`);

  return { token, url: inviteUrl, invite };
}

async function list(options) {
  // Use SCAN instead of KEYS to avoid blocking Redis on large datasets
  const keys = [];
  let cursor = '0';
  do {
    const [nextCursor, batch] = await redis.scan(cursor, 'MATCH', 'invite:*', 'COUNT', 100);
    cursor = nextCursor;
    keys.push(...batch);
  } while (cursor !== '0');

  if (keys.length === 0) {
    console.log('\nNo invites found.\n');
    return;
  }

  const invites = [];
  for (const key of keys) {
    const data = await redis.get(key);
    if (data) {
      const invite = JSON.parse(data);
      // Update expired status
      if (invite.status === 'pending' && new Date(invite.expiresAt) < new Date()) {
        invite.status = 'expired';
      }
      invites.push(invite);
    }
  }

  // Filter by status if specified
  let filtered = invites;
  if (options.status) {
    filtered = invites.filter(i => i.status === options.status);
  }

  // Sort by creation date (newest first)
  filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  console.log(`\nInvites (${filtered.length} of ${invites.length}):\n`);
  console.log('TOKEN            STATUS    EXPIRES              LABEL');
  console.log('-'.repeat(70));

  for (const invite of filtered) {
    const status = invite.status.padEnd(9);
    const expires = new Date(invite.expiresAt).toISOString().slice(0, 19).replace('T', ' ');
    const label = invite.label || '-';
    console.log(`${invite.token}  ${status} ${expires}  ${label}`);
  }
  console.log('');
}

async function info(token) {
  const data = await redis.get(`invite:${token}`);

  if (!data) {
    console.error(`\nInvite not found: ${token}\n`);
    process.exit(1);
  }

  const invite = JSON.parse(data);

  // Update expired status
  if (invite.status === 'pending' && new Date(invite.expiresAt) < new Date()) {
    invite.status = 'expired';
  }

  console.log('\nInvite Details:\n');
  console.log(`Token:     ${invite.token}`);
  console.log(`Status:    ${invite.status}`);
  console.log(`Created:   ${invite.createdAt}`);
  console.log(`Expires:   ${invite.expiresAt}`);
  console.log(`Uses:      ${invite.useCount} / ${invite.maxUses}`);
  console.log(`Label:     ${invite.label || '-'}`);
  console.log(`Created By: ${invite.createdBy}`);

  if (invite.sessions && invite.sessions.length > 0) {
    console.log(`\nSessions (${invite.sessions.length}):`);
    for (const session of invite.sessions) {
      console.log(`  - ${session.startedAt} | ${session.endReason} | ${session.ip}`);
      console.log(`    Queue wait: ${Math.round(session.queueWaitMs / 1000)}s | UA: ${session.userAgent?.slice(0, 50)}...`);
    }
  }
  console.log('');
}

async function revoke(token) {
  const data = await redis.get(`invite:${token}`);

  if (!data) {
    console.error(`\nInvite not found: ${token}\n`);
    process.exit(1);
  }

  const invite = JSON.parse(data);
  invite.status = 'revoked';

  // Keep same TTL
  const ttl = await redis.ttl(`invite:${token}`);
  await redis.set(`invite:${token}`, JSON.stringify(invite), 'EX', ttl > 0 ? ttl : 86400);

  console.log(`\nInvite revoked: ${token}\n`);
}

// =============================================================================
// CLI Argument Parsing
// =============================================================================

function parseArgs() {
  const args = process.argv.slice(2);
  const command = args[0];
  const options = {};

  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
      options[key] = value;
    } else if (!options._positional) {
      options._positional = args[i];
    }
  }

  return { command, options };
}

function showHelp() {
  console.log(`
Invite CLI - Generate and manage demo invite URLs

Usage:
  node invite-cli.js <command> [options]

Commands:
  generate              Create a new invite URL
    --expires <duration>  Expiration time (default: 48h)
                         Formats: 30m, 48h, 7d, 2w
    --token <token>      Custom token for VIP users (4-64 chars, URL-safe)
    --label <text>       Optional label for identification

  list                  List all invites
    --status <status>    Filter by status: pending, used, expired, revoked

  info <token>          Show details for an invite

  revoke <token>        Revoke an invite

Examples:
  node invite-cli.js generate --expires 7d --label "Conference demo"
  node invite-cli.js generate --expires 30d --token "VIP-JOHN" --label "VIP John"
  node invite-cli.js list --status pending
  node invite-cli.js info abc123
  node invite-cli.js revoke abc123
`);
}

// =============================================================================
// Main
// =============================================================================

async function main() {
  const { command, options } = parseArgs();

  try {
    switch (command) {
      case 'generate':
        await generate(options);
        break;
      case 'list':
        await list(options);
        break;
      case 'info':
        if (!options._positional) {
          console.error('Error: Token required. Usage: invite-cli.js info <token>');
          process.exit(1);
        }
        await info(options._positional);
        break;
      case 'revoke':
        if (!options._positional) {
          console.error('Error: Token required. Usage: invite-cli.js revoke <token>');
          process.exit(1);
        }
        await revoke(options._positional);
        break;
      case 'help':
      case '--help':
      case '-h':
      case undefined:
        showHelp();
        break;
      default:
        console.error(`Unknown command: ${command}`);
        showHelp();
        process.exit(1);
    }
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  } finally {
    redis.quit();
  }
}

main();
