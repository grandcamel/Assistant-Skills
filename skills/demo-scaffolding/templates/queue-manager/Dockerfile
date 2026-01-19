FROM node:20-alpine

# Install curl for healthcheck and python3 for scripts
RUN apk add --no-cache curl python3 py3-pip docker-cli

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Create directories for session management
RUN mkdir -p /run/session-env && \
    chown -R nodejs:nodejs /run/session-env

EXPOSE 3000

# Run as non-root but with docker group access
CMD ["node", "--require", "./instrumentation.js", "server.js"]
