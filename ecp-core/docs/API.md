# ECP REST API

This document provides details on the REST API for the Echo Coordination Protocol (ECP). The API allows for programmatic interaction with the ECP system, enabling the recording of events, submission of classifications, and retrieval of consensus scores.

## Running the API Server

To run the API server, execute the following command from the `reference-implementation` directory:

```bash
python3 -m ai_coordination.api.server
```

The server will be available at `http://localhost:8000`.

## Endpoints

### POST /events

Records a new event in the ECP system.

**Request Body:**

```json
{
  "event_type": "string",
  "description": "string",
  "payload": {},
  "context": {}
}
```

**Response:**

```json
{
  "event_id": "string"
}
```

### POST /classifications

Adds a new classification to an existing event.

**Request Body:**

```json
{
  "event_id": "string",
  "classification": {}
}
```

**Response:**

```json
{
  "message": "string"
}
```

### GET /consensus/{event_id}

Calculates and returns the consensus score for a given event.

**Response:**

```json
{
  "event_id": "string",
  "timestamp": "string",
  "divergence_score": "float",
  "max_pairwise_divergence": "float",
  "requires_human_review": "boolean",
  "agent_scores": {},
  "trigger_reason": "string"
}
```
