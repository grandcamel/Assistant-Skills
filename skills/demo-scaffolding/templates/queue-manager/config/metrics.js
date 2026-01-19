/**
 * OpenTelemetry metrics configuration.
 */

let metrics, trace;
try {
  const api = require('@opentelemetry/api');
  metrics = api.metrics;
  trace = api.trace;
} catch (_e) {
  // OTel not available, will use no-op implementations
}

let meter, queueSizeGauge, sessionsActiveGauge, sessionsStartedCounter,
    sessionsEndedCounter, sessionDurationHistogram, queueWaitHistogram,
    ttydSpawnHistogram, invitesValidatedCounter, sandboxCleanupHistogram;

/**
 * Initialize metrics with observable callbacks.
 * @param {Function} getQueueLength - Function to get current queue length
 * @param {Function} getActiveSessionCount - Function to get active session count (0 or 1)
 */
function initMetrics(getQueueLength, getActiveSessionCount) {
  if (!metrics) return;

  meter = metrics.getMeter('{{DEMO_NAME}}-queue-manager');

  // Gauges
  queueSizeGauge = meter.createObservableGauge('demo_queue_size', {
    description: 'Current number of clients in queue',
  });
  sessionsActiveGauge = meter.createObservableGauge('demo_sessions_active', {
    description: 'Number of currently active sessions',
  });

  // Counters
  sessionsStartedCounter = meter.createCounter('demo_sessions_started_total', {
    description: 'Total number of sessions started',
  });
  sessionsEndedCounter = meter.createCounter('demo_sessions_ended_total', {
    description: 'Total number of sessions ended',
  });
  invitesValidatedCounter = meter.createCounter('demo_invites_validated_total', {
    description: 'Total number of invite validations',
  });

  // Histograms
  sessionDurationHistogram = meter.createHistogram('demo_session_duration_seconds', {
    description: 'Session duration in seconds',
    unit: 's',
  });
  queueWaitHistogram = meter.createHistogram('demo_queue_wait_seconds', {
    description: 'Time spent waiting in queue',
    unit: 's',
  });
  ttydSpawnHistogram = meter.createHistogram('demo_ttyd_spawn_seconds', {
    description: 'Time to spawn ttyd process',
    unit: 's',
  });
  sandboxCleanupHistogram = meter.createHistogram('demo_sandbox_cleanup_seconds', {
    description: 'Sandbox cleanup duration',
    unit: 's',
  });

  // Register observable callbacks
  queueSizeGauge.addCallback((result) => {
    result.observe(getQueueLength());
  });
  sessionsActiveGauge.addCallback((result) => {
    result.observe(getActiveSessionCount());
  });
}

/**
 * Get the OpenTelemetry tracer.
 * @returns {Tracer|null} Tracer instance or null if OTel not available
 */
function getTracer() {
  return trace ? trace.getTracer('{{DEMO_NAME}}-queue-manager') : null;
}

module.exports = {
  initMetrics,
  getTracer,
  get sessionsStartedCounter() { return sessionsStartedCounter; },
  get sessionsEndedCounter() { return sessionsEndedCounter; },
  get sessionDurationHistogram() { return sessionDurationHistogram; },
  get queueWaitHistogram() { return queueWaitHistogram; },
  get ttydSpawnHistogram() { return ttydSpawnHistogram; },
  get invitesValidatedCounter() { return invitesValidatedCounter; },
  get sandboxCleanupHistogram() { return sandboxCleanupHistogram; }
};
