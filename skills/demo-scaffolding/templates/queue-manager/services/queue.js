/**
 * Queue management service.
 */

const config = require('../config');
const state = require('./state');
const { validateInvite } = require('./invite');
const { generateSessionToken, startSession, findClientWs } = require('./session');

/**
 * Join the queue.
 * @param {Object} redis - Redis client
 * @param {WebSocket} ws - WebSocket connection
 * @param {Object} client - Client object
 * @param {string|null} inviteToken - Invite token
 * @param {Function} processQueueFn - Queue processing callback
 */
async function joinQueue(redis, ws, client, inviteToken, processQueueFn) {
  const activeSession = state.getActiveSession();

  // Check if this is a reconnection to an active session (grace period)
  if (activeSession && activeSession.awaitingReconnect &&
      activeSession.inviteToken === inviteToken && activeSession.ip === client.ip) {

    // Prevent concurrent reconnection attempts
    if (state.isReconnectionInProgress()) {
      sendError(ws, 'Reconnection already in progress');
      return;
    }

    state.setReconnectionInProgress(true);
    try {
      console.log(`Client ${client.id} reconnecting to session ${activeSession.sessionId} during grace period`);

      // Cancel the grace period timeout
      state.clearDisconnectGraceTimeout();

      // Update session with new client
      activeSession.clientId = client.id;
      activeSession.awaitingReconnect = false;
      delete activeSession.disconnectedAt;

      // Give client the existing session token
      client.inviteToken = inviteToken;
      client.state = 'active';
      client.pendingSessionToken = activeSession.sessionToken;

      // Send session info to client
      ws.send(JSON.stringify({
        type: 'session_token',
        session_token: activeSession.sessionToken
      }));
      ws.send(JSON.stringify({
        type: 'session_starting',
        terminal_url: '/terminal',
        expires_at: activeSession.expiresAt.toISOString(),
        session_token: activeSession.sessionToken,
        reconnected: true
      }));

      console.log(`Session ${activeSession.sessionId} reconnected successfully`);
    } finally {
      state.setReconnectionInProgress(false);
    }
    return;
  }

  // Check if already in queue
  if (state.queue.includes(client.id)) {
    sendError(ws, 'Already in queue');
    return;
  }

  // Validate invite token if provided
  if (inviteToken) {
    const validation = await validateInvite(redis, inviteToken, client.ip);
    if (!validation.valid) {
      ws.send(JSON.stringify({
        type: 'invite_invalid',
        reason: validation.reason,
        message: validation.message
      }));
      return;
    }
    client.inviteToken = inviteToken;
    client.inviteData = validation.data;
    console.log(`Client ${client.id} has valid invite: ${inviteToken.slice(0, 8)}...`);
  }

  // Check queue size limit
  if (state.queue.length >= config.MAX_QUEUE_SIZE) {
    ws.send(JSON.stringify({
      type: 'queue_full',
      message: 'Queue is full. Please try again later.'
    }));
    return;
  }

  // Generate pending session token immediately (allows page refresh while in queue)
  const pendingToken = generateSessionToken(client.id);
  state.pendingSessionTokens.set(pendingToken, {
    clientId: client.id,
    inviteToken: inviteToken || null,
    ip: client.ip,
    createdAt: new Date()
  });
  client.pendingSessionToken = pendingToken;

  // Send token immediately so client can set cookie
  ws.send(JSON.stringify({
    type: 'session_token',
    session_token: pendingToken
  }));

  // Add to queue
  state.queue.push(client.id);
  client.state = 'queued';
  client.joinedAt = new Date();

  console.log(`Client ${client.id} joined queue (position ${state.queue.length})`);

  // If no active session and first in queue, start immediately
  if (!state.getActiveSession() && state.queue[0] === client.id) {
    startSession(redis, ws, client, processQueueFn);
  } else {
    sendQueuePosition(ws, client);
  }

  broadcastQueueUpdate();
}

/**
 * Leave the queue.
 * @param {WebSocket} ws - WebSocket connection
 * @param {Object} client - Client object
 */
function leaveQueue(ws, client) {
  const queueIndex = state.queue.indexOf(client.id);
  if (queueIndex !== -1) {
    state.queue.splice(queueIndex, 1);
    client.state = 'connected';
    console.log(`Client ${client.id} left queue`);

    ws.send(JSON.stringify({ type: 'left_queue' }));
    broadcastQueueUpdate();
  }
}

/**
 * Send queue position to a client.
 * @param {WebSocket} ws - WebSocket connection
 * @param {Object} client - Client object
 */
function sendQueuePosition(ws, client) {
  const position = state.queue.indexOf(client.id) + 1;
  const estimatedWait = position * config.AVERAGE_SESSION_MINUTES;

  ws.send(JSON.stringify({
    type: 'queue_position',
    position: position,
    estimated_wait: `${estimatedWait} minutes`,
    queue_size: state.queue.length
  }));
}

/**
 * Broadcast queue update to all queued clients.
 */
function broadcastQueueUpdate() {
  state.clients.forEach((client, ws) => {
    if (client.state === 'queued') {
      sendQueuePosition(ws, client);
    }
  });
}

/**
 * Process the queue (start next session if available).
 * @param {Object} redis - Redis client
 */
function processQueue(redis) {
  const activeSession = state.getActiveSession();
  if (activeSession || state.queue.length === 0) return;

  const nextClientId = state.queue[0];
  const nextClientWs = findClientWs(nextClientId);

  if (nextClientWs) {
    const client = state.clients.get(nextClientWs);
    startSession(redis, nextClientWs, client, () => processQueue(redis));
  } else {
    // Client disconnected, remove and try next
    state.queue.shift();
    processQueue(redis);
  }
}

/**
 * Send error message to client.
 * @param {WebSocket} ws - WebSocket connection
 * @param {string} message - Error message
 */
function sendError(ws, message) {
  ws.send(JSON.stringify({ type: 'error', message }));
}

module.exports = {
  joinQueue,
  leaveQueue,
  sendQueuePosition,
  broadcastQueueUpdate,
  processQueue
};
