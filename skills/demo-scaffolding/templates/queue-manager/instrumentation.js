/**
 * OpenTelemetry Instrumentation Bootstrap
 *
 * This module initializes OpenTelemetry SDK and auto-instrumentation
 * for Express, HTTP, WebSocket, and ioredis.
 *
 * Must be loaded before any other modules via --require flag:
 *   node --require ./instrumentation.js server.js
 */

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-proto');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-proto');
const { Resource } = require('@opentelemetry/resources');
const { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } = require('@opentelemetry/semantic-conventions');

// Only initialize if OTEL endpoint is configured
const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;

if (otlpEndpoint) {
  const resource = new Resource({
    [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || '{{DEMO_NAME}}-queue-manager',
    [ATTR_SERVICE_VERSION]: '1.0.0',
    'deployment.environment': process.env.NODE_ENV || 'production',
  });

  const sdk = new NodeSDK({
    resource: resource,
    traceExporter: new OTLPTraceExporter({
      url: `${otlpEndpoint}/v1/traces`,
    }),
    metricReader: new PeriodicExportingMetricReader({
      exporter: new OTLPMetricExporter({
        url: `${otlpEndpoint}/v1/metrics`,
      }),
      exportIntervalMillis: 15000, // Export every 15 seconds
    }),
    instrumentations: [
      getNodeAutoInstrumentations({
        // Ignore health check requests from traces
        '@opentelemetry/instrumentation-http': {
          ignoreIncomingRequestHook: (request) => {
            const url = request.url || '';
            // Ignore health checks and favicon
            if (url === '/api/health' || url === '/favicon.ico') {
              return true;
            }
            return false;
          },
        },
        // Configure Express instrumentation
        '@opentelemetry/instrumentation-express': {
          enabled: true,
        },
        // Configure WebSocket instrumentation
        '@opentelemetry/instrumentation-ws': {
          enabled: true,
        },
        // Configure ioredis instrumentation
        '@opentelemetry/instrumentation-ioredis': {
          enabled: true,
        },
        // Disable file system instrumentation (too noisy)
        '@opentelemetry/instrumentation-fs': {
          enabled: false,
        },
      }),
    ],
  });

  sdk.start();
  console.log('OpenTelemetry instrumentation started');

  // Graceful shutdown
  process.on('SIGTERM', () => {
    sdk.shutdown()
      .then(() => console.log('OpenTelemetry shut down'))
      .catch((err) => console.error('Error shutting down OpenTelemetry:', err))
      .finally(() => process.exit(0));
  });
} else {
  console.log('OpenTelemetry disabled (OTEL_EXPORTER_OTLP_ENDPOINT not set)');
}
