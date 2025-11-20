# OMEGA Echo - Hardened Container Image
# Provides process isolation and minimal attack surface

FROM node:18-alpine

# Security: Run as non-root user
RUN addgroup -g 1001 omega && \
    adduser -D -u 1001 -G omega omega

# Set working directory
WORKDIR /app

# Copy package files first (for better layer caching)
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application code
COPY --chown=omega:omega . .

# Create cosmic_status directory
RUN mkdir -p /app/cosmic_status && \
    chown -R omega:omega /app/cosmic_status

# Switch to non-root user
USER omega

# Set environment defaults
ENV NODE_ENV=production

# Expose port (if needed for future features)
# EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "console.log('healthy')" || exit 1

# Start the embryo
CMD ["node", "index.js"]
