/**
 * Shared state management for the queue manager.
 */

// Client connections: ws -> { id, state, joinedAt, ip, userAgent, inviteToken, pendingSessionToken }
const clients = new Map();

// Queue: Array of client IDs waiting
const queue = [];

// Active session: { clientId, sessionId, sessionToken, ttydProcess, startedAt, expiresAt, inviteToken, ip, userAgent, queueWaitMs, errors, envFileCleanup, hardTimeout, awaitingReconnect, disconnectedAt }
let activeSession = null;

// Session tokens: sessionToken -> sessionId (for Grafana auth)
const sessionTokens = new Map();

// Pending session tokens: sessionToken -> { clientId, inviteToken, ip, createdAt } (for queue/pending state)
const pendingSessionTokens = new Map();

// Disconnect grace period timeout
let disconnectGraceTimeout = null;

// Reconnection lock to prevent concurrent reconnection attempts
let reconnectionInProgress = false;

/**
 * Get the current active session.
 * @returns {Object|null} Active session or null
 */
function getActiveSession() {
  return activeSession;
}

/**
 * Set the active session.
 * @param {Object|null} session - Session object or null to clear
 */
function setActiveSession(session) {
  activeSession = session;
}

/**
 * Get reconnection in progress flag.
 * @returns {boolean} Whether reconnection is in progress
 */
function isReconnectionInProgress() {
  return reconnectionInProgress;
}

/**
 * Set reconnection in progress flag.
 * @param {boolean} inProgress - Whether reconnection is in progress
 */
function setReconnectionInProgress(inProgress) {
  reconnectionInProgress = inProgress;
}

/**
 * Get the disconnect grace timeout.
 * @returns {Timeout|null} The timeout or null
 */
function getDisconnectGraceTimeout() {
  return disconnectGraceTimeout;
}

/**
 * Set the disconnect grace timeout.
 * @param {Timeout|null} timeout - The timeout or null to clear
 */
function setDisconnectGraceTimeout(timeout) {
  disconnectGraceTimeout = timeout;
}

/**
 * Clear the disconnect grace timeout if set.
 */
function clearDisconnectGraceTimeout() {
  if (disconnectGraceTimeout) {
    clearTimeout(disconnectGraceTimeout);
    disconnectGraceTimeout = null;
  }
}

module.exports = {
  clients,
  queue,
  sessionTokens,
  pendingSessionTokens,
  getActiveSession,
  setActiveSession,
  isReconnectionInProgress,
  setReconnectionInProgress,
  getDisconnectGraceTimeout,
  setDisconnectGraceTimeout,
  clearDisconnectGraceTimeout
};
