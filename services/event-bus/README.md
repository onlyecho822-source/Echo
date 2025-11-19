# Event Bus Service

Asynchronous event messaging for Echo Nexus.

## Overview

Provides pub/sub messaging between all Echo Nexus components.

## Running

```bash
# Development
python -m echo_nexus.services.event_bus

# Production
docker run -p 5672:5672 echo-nexus/event-bus
```

## Features

- Topic-based routing
- Message persistence
- Dead letter queues
- Event replay
- At-least-once delivery

## Topics

- `capsule.created` - New capsule created
- `engine.started` - Engine started
- `engine.stopped` - Engine stopped
- `insight.generated` - New insight

---

*∇θ — events flowing.*
