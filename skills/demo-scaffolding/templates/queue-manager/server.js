/**
 * {{PRODUCT}} Demo Queue Manager
 *
 * Manages single-user demo sessions with queue/waitlist functionality.
 * Supports invite-based access control with detailed session tracking.
 *
 * WebSocket Protocol:
 *   Client -> Server:
 *     { type: "join_queue", inviteToken?: "token" }
 *     { type: "leave_queue" }
 *     { type: "heartbeat" }
 *
 *   Server -> Client:
 *     { type: "queue_position", position: N, estimated_wait: "X minutes", queue_size: N }
 *     { type: "session_starting", terminal_url: "/terminal" }
 *     { type: "session_active", expires_at: "ISO timestamp" }
 *     { type: "session_warning", minutes_remaining: 5 }
 *     { type: "session_ended", reason: "timeout" | "disconnected" | "error" }
 *     { type: "invite_invalid", reason: "not_found" | "expired" | "used" | "revoked", message: "..." }
 *     { type: "error", message: "..." }
 */

const express = require('express');
const { WebSocketServer } = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const Redis = require('ioredis');
const cookieParser = require('cookie-parser');
const helmet = require('helmet');

// Configuration and services
const config = require('./config');
const { initMetrics } = require('./config/metrics');
const state = require('./services/state');
const { processQueue } = require('./services/queue');
const { endSession } = require('./services/session');
const { cleanupRateLimits: cleanupInviteRateLimits } = require('./services/invite');

// Routes
const healthRoutes = require('./routes/health');
const sessionRoutes = require('./routes/session');
const scenarioRoutes = require('./routes/scenarios');

// Handlers
const websocketHandlers = require('./handlers/websocket');

// Initialize services
const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/api/ws' });
const redis = new Redis(config.REDIS_URL);

// Handle Redis connection errors
redis.on('error', (err) => {
  console.error('Redis connection error:', err.message);
});

redis.on('connect', () => {
  console.log('Connected to Redis');
});

// Initialize metrics
initMetrics(
  () => state.queue.length,
  () => state.getActiveSession() ? 1 : 0
);

// Middleware
app.use(express.json());
app.use(cookieParser());

// Content-Type validation for POST/PUT/PATCH requests
app.use((req, res, next) => {
  const methodsRequiringBody = ['POST', 'PUT', 'PATCH'];
  if (methodsRequiringBody.includes(req.method)) {
    const contentType = req.headers['content-type'];
    const hasBody = req.headers['content-length'] && req.headers['content-length'] !== '0';
    if (hasBody && (!contentType || !contentType.includes('application/json'))) {
      return res.status(415).json({ error: 'Content-Type must be application/json' });
    }
  }
  next();
});

// Security headers via Helmet
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "blob:"],
      connectSrc: ["'self'", "wss:", "ws:"],
      frameSrc: ["'self'"],
      frameAncestors: ["'self'"],
    }
  },
  crossOriginEmbedderPolicy: false,
  crossOriginOpenerPolicy: { policy: "same-origin-allow-popups" },
}));

// Serve static files (CSS, JS)
app.use('/static', express.static(path.join(__dirname, 'static')));

// Register routes
healthRoutes.register(app);
sessionRoutes.register(app, redis);
scenarioRoutes.register(app);

// Set up WebSocket handlers
websocketHandlers.setup(wss, redis);

// Validate SESSION_SECRET in production
if (config.SESSION_SECRET === 'change-me-in-production') {
  if (process.env.NODE_ENV === 'production') {
    console.error('FATAL: SESSION_SECRET must be set in production');
    process.exit(1);
  } else {
    console.warn('WARNING: Using default SESSION_SECRET. Set SESSION_SECRET env var for secure sessions.');
  }
}

// Ensure session env directory exists
try {
  fs.mkdirSync(config.SESSION_ENV_CONTAINER_PATH, { recursive: true });
  console.log(`Session env directory ready: ${config.SESSION_ENV_CONTAINER_PATH}`);
} catch (err) {
  console.error(`Warning: Could not create session env directory: ${err.message}`);
}

// Periodic cleanup of stale rate limit entries (every 5 minutes)
setInterval(() => {
  websocketHandlers.cleanupRateLimits();
  cleanupInviteRateLimits();
}, 5 * 60 * 1000);

// Start server
server.listen(config.PORT, () => {
  console.log(`Queue manager listening on port ${config.PORT}`);
  console.log(`Session timeout: ${config.SESSION_TIMEOUT_MINUTES} minutes`);
  console.log(`Max queue size: ${config.MAX_QUEUE_SIZE}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Shutting down...');

  // Clear grace period timeout
  state.clearDisconnectGraceTimeout();

  if (state.getActiveSession()) {
    await endSession(redis, 'shutdown', () => processQueue(redis));
  }

  wss.close();
  server.close();
  redis.quit();

  process.exit(0);
});
