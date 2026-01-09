# 🧪 Sherlock Hub API Test Suite

**Comprehensive testing guide for all Sherlock Hub endpoints**

**Status:** Ready for Execution
**Last Updated:** December 17, 2025

---

## 📋 Test Environment Setup

### Prerequisites
```bash
# Start Sherlock Hub
cd /home/ubuntu/Echo/sherlock-hub
docker-compose up

# Wait for services to be ready (30-60 seconds)
# You should see: "Application startup complete"
```

### Test Tools
- **curl** - Command-line HTTP client (pre-installed)
- **jq** - JSON processor (optional, for pretty-printing)
- **Postman** - GUI client (optional)

### Base URL
```
http://localhost:8000
```

---

## 🏥 Health & Status Endpoints

### Test 1: API Health Check

**Endpoint:** `GET /health`

**Command:**
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-17T19:45:00Z",
  "version": "1.0.0"
}
```

**Success Criteria:**
- Status code: 200
- Response contains "healthy"
- Timestamp is recent

### Test 2: API Documentation

**Endpoint:** `GET /docs`

**Command:**
```bash
curl -X GET http://localhost:8000/docs
```

**Expected Response:**
- HTML page with Swagger UI
- All endpoints listed
- Interactive documentation

**Success Criteria:**
- Status code: 200
- HTML content returned
- Swagger UI loads

---

## 👥 Entity Management Endpoints

### Test 3: Create Entity

**Endpoint:** `POST /api/entities`

**Command:**
```bash
curl -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Person",
    "name": "John Doe",
    "properties": {
      "email": "john@example.com",
      "role": "Engineer",
      "department": "Engineering"
    }
  }'
```

**Expected Response:**
```json
{
  "id": "entity-123",
  "type": "Person",
  "name": "John Doe",
  "properties": {
    "email": "john@example.com",
    "role": "Engineer",
    "department": "Engineering"
  },
  "created_at": "2025-12-17T19:45:00Z",
  "updated_at": "2025-12-17T19:45:00Z"
}
```

**Success Criteria:**
- Status code: 201 (Created)
- Response includes entity ID
- All properties preserved
- Timestamps present

### Test 4: Get Entity

**Endpoint:** `GET /api/entities/{id}`

**Command:**
```bash
# Replace entity-123 with actual ID from Test 3
curl -X GET http://localhost:8000/api/entities/entity-123
```

**Expected Response:**
```json
{
  "id": "entity-123",
  "type": "Person",
  "name": "John Doe",
  "properties": {
    "email": "john@example.com",
    "role": "Engineer",
    "department": "Engineering"
  },
  "created_at": "2025-12-17T19:45:00Z",
  "updated_at": "2025-12-17T19:45:00Z"
}
```

**Success Criteria:**
- Status code: 200
- Entity data matches what was created
- All fields present

### Test 5: List Entities

**Endpoint:** `GET /api/entities`

**Command:**
```bash
curl -X GET http://localhost:8000/api/entities
```

**Expected Response:**
```json
{
  "total": 1,
  "page": 1,
  "limit": 10,
  "entities": [
    {
      "id": "entity-123",
      "type": "Person",
      "name": "John Doe",
      "properties": { ... }
    }
  ]
}
```

**Success Criteria:**
- Status code: 200
- Returns array of entities
- Includes pagination info
- At least 1 entity (from Test 3)

### Test 6: Update Entity

**Endpoint:** `PUT /api/entities/{id}`

**Command:**
```bash
curl -X PUT http://localhost:8000/api/entities/entity-123 \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "email": "john.doe@example.com",
      "role": "Senior Engineer"
    }
  }'
```

**Expected Response:**
```json
{
  "id": "entity-123",
  "type": "Person",
  "name": "John Doe",
  "properties": {
    "email": "john.doe@example.com",
    "role": "Senior Engineer",
    "department": "Engineering"
  },
  "updated_at": "2025-12-17T19:46:00Z"
}
```

**Success Criteria:**
- Status code: 200
- Properties updated
- Updated_at timestamp changed
- Other properties preserved

### Test 7: Delete Entity

**Endpoint:** `DELETE /api/entities/{id}`

**Command:**
```bash
curl -X DELETE http://localhost:8000/api/entities/entity-123
```

**Expected Response:**
```json
{
  "message": "Entity deleted successfully",
  "id": "entity-123"
}
```

**Success Criteria:**
- Status code: 200
- Confirmation message
- Entity ID confirmed

---

## 🔗 Relationship Endpoints

### Test 8: Create Relationship

**Endpoint:** `POST /api/relationships`

**Setup:**
First, create two entities:
```bash
# Create Person 1
curl -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Person",
    "name": "Alice Smith",
    "properties": {"role": "Manager"}
  }'
# Save the ID as ALICE_ID

# Create Person 2
curl -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Person",
    "name": "Bob Johnson",
    "properties": {"role": "Engineer"}
  }'
# Save the ID as BOB_ID
```

**Command:**
```bash
curl -X POST http://localhost:8000/api/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "from_id": "ALICE_ID",
    "to_id": "BOB_ID",
    "type": "manages",
    "properties": {
      "since": "2025-01-01",
      "team": "Engineering"
    }
  }'
```

**Expected Response:**
```json
{
  "id": "rel-456",
  "from_id": "ALICE_ID",
  "to_id": "BOB_ID",
  "type": "manages",
  "properties": {
    "since": "2025-01-01",
    "team": "Engineering"
  },
  "created_at": "2025-12-17T19:47:00Z"
}
```

**Success Criteria:**
- Status code: 201
- Relationship ID created
- Both entities linked
- Properties preserved

### Test 9: Find Path Between Entities

**Endpoint:** `GET /api/paths/{from_id}/{to_id}`

**Command:**
```bash
curl -X GET http://localhost:8000/api/paths/ALICE_ID/BOB_ID
```

**Expected Response:**
```json
{
  "from_id": "ALICE_ID",
  "to_id": "BOB_ID",
  "paths": [
    {
      "length": 1,
      "nodes": ["ALICE_ID", "BOB_ID"],
      "relationships": [
        {
          "type": "manages",
          "properties": { ... }
        }
      ]
    }
  ]
}
```

**Success Criteria:**
- Status code: 200
- Path found between entities
- Relationship type correct
- Path length accurate

### Test 10: Get Related Entities

**Endpoint:** `GET /api/entities/{id}/related`

**Command:**
```bash
curl -X GET http://localhost:8000/api/entities/ALICE_ID/related
```

**Expected Response:**
```json
{
  "entity_id": "ALICE_ID",
  "related": [
    {
      "entity": {
        "id": "BOB_ID",
        "type": "Person",
        "name": "Bob Johnson"
      },
      "relationship": {
        "type": "manages",
        "properties": { ... }
      }
    }
  ]
}
```

**Success Criteria:**
- Status code: 200
- Related entities listed
- Relationship info included
- Correct entity returned

---

## 🔍 Search Endpoints

### Test 11: Full-Text Search

**Endpoint:** `GET /api/search?q=term`

**Command:**
```bash
curl -X GET "http://localhost:8000/api/search?q=Engineer"
```

**Expected Response:**
```json
{
  "query": "Engineer",
  "total": 2,
  "results": [
    {
      "id": "entity-123",
      "type": "Person",
      "name": "John Doe",
      "match_score": 0.95,
      "matched_fields": ["role"]
    },
    {
      "id": "BOB_ID",
      "type": "Person",
      "name": "Bob Johnson",
      "match_score": 0.95,
      "matched_fields": ["role"]
    }
  ]
}
```

**Success Criteria:**
- Status code: 200
- Results returned
- Match scores present
- Matched fields identified

### Test 12: Advanced Search

**Endpoint:** `GET /api/search/advanced`

**Command:**
```bash
curl -X GET "http://localhost:8000/api/search/advanced?type=Person&role=Engineer"
```

**Expected Response:**
```json
{
  "filters": {
    "type": "Person",
    "role": "Engineer"
  },
  "total": 1,
  "results": [
    {
      "id": "BOB_ID",
      "type": "Person",
      "name": "Bob Johnson",
      "properties": {
        "role": "Engineer"
      }
    }
  ]
}
```

**Success Criteria:**
- Status code: 200
- Filters applied correctly
- Matching results returned
- No false positives

---

## 💬 Q&A Endpoints

### Test 13: Ask Question

**Endpoint:** `POST /api/qa`

**Command:**
```bash
curl -X POST http://localhost:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who manages Bob Johnson?"
  }'
```

**Expected Response:**
```json
{
  "id": "qa-789",
  "question": "Who manages Bob Johnson?",
  "answer": "Alice Smith manages Bob Johnson. She has been managing him since 2025-01-01 in the Engineering team.",
  "confidence": 0.92,
  "sources": [
    {
      "entity_id": "ALICE_ID",
      "entity_name": "Alice Smith",
      "relationship_type": "manages"
    }
  ],
  "created_at": "2025-12-17T19:48:00Z"
}
```

**Success Criteria:**
- Status code: 200
- Question answered
- Confidence score present
- Sources cited

### Test 14: Get Q&A History

**Endpoint:** `GET /api/qa/{id}`

**Command:**
```bash
curl -X GET http://localhost:8000/api/qa/qa-789
```

**Expected Response:**
```json
{
  "id": "qa-789",
  "question": "Who manages Bob Johnson?",
  "answer": "Alice Smith manages Bob Johnson...",
  "confidence": 0.92,
  "sources": [ ... ],
  "created_at": "2025-12-17T19:48:00Z"
}
```

**Success Criteria:**
- Status code: 200
- Q&A record retrieved
- All fields present
- Answer consistent

---

## 📊 Graph Visualization Endpoints

### Test 15: Get Graph Data

**Endpoint:** `GET /api/graph`

**Command:**
```bash
curl -X GET http://localhost:8000/api/graph
```

**Expected Response:**
```json
{
  "nodes": [
    {
      "id": "ALICE_ID",
      "label": "Alice Smith",
      "type": "Person",
      "properties": { ... }
    },
    {
      "id": "BOB_ID",
      "label": "Bob Johnson",
      "type": "Person",
      "properties": { ... }
    }
  ],
  "edges": [
    {
      "id": "rel-456",
      "source": "ALICE_ID",
      "target": "BOB_ID",
      "label": "manages",
      "properties": { ... }
    }
  ]
}
```

**Success Criteria:**
- Status code: 200
- Nodes and edges returned
- Proper graph structure
- All entities included

---

## ⚙️ System Endpoints

### Test 16: System Status

**Endpoint:** `GET /api/system/status`

**Command:**
```bash
curl -X GET http://localhost:8000/api/system/status
```

**Expected Response:**
```json
{
  "status": "operational",
  "database": "connected",
  "cache": "operational",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "entities_count": 5,
  "relationships_count": 2
}
```

**Success Criteria:**
- Status code: 200
- All systems operational
- Database connected
- Accurate counts

### Test 17: System Metrics

**Endpoint:** `GET /api/system/metrics`

**Command:**
```bash
curl -X GET http://localhost:8000/api/system/metrics
```

**Expected Response:**
```json
{
  "requests_total": 150,
  "requests_per_minute": 2.5,
  "average_response_time_ms": 45,
  "database_queries": 300,
  "cache_hits": 120,
  "cache_misses": 30,
  "errors": 0
}
```

**Success Criteria:**
- Status code: 200
- Metrics present
- Response times reasonable
- Error count low

---

## 🧪 Integration Test Suite

### Test 18: Complete Workflow

This test simulates a complete user workflow:

```bash
#!/bin/bash

# 1. Create entities
echo "Creating entities..."
ALICE=$(curl -s -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Person",
    "name": "Alice",
    "properties": {"role": "Manager"}
  }' | jq -r '.id')

BOB=$(curl -s -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Person",
    "name": "Bob",
    "properties": {"role": "Engineer"}
  }' | jq -r '.id')

echo "Created entities: $ALICE, $BOB"

# 2. Create relationship
echo "Creating relationship..."
curl -s -X POST http://localhost:8000/api/relationships \
  -H "Content-Type: application/json" \
  -d "{
    \"from_id\": \"$ALICE\",
    \"to_id\": \"$BOB\",
    \"type\": \"manages\"
  }" | jq .

# 3. Search
echo "Searching..."
curl -s -X GET "http://localhost:8000/api/search?q=Engineer" | jq .

# 4. Ask question
echo "Asking question..."
curl -s -X POST http://localhost:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who manages Bob?"
  }' | jq .

# 5. Get graph
echo "Getting graph..."
curl -s -X GET http://localhost:8000/api/graph | jq .

echo "Integration test complete!"
```

**Success Criteria:**
- All operations succeed
- Data flows correctly
- Relationships work
- Search finds results
- Q&A answers questions
- Graph renders correctly

---

## 📈 Performance Tests

### Test 19: Bulk Entity Creation

**Objective:** Create 1000 entities and measure performance

```bash
#!/bin/bash

echo "Creating 1000 entities..."
START=$(date +%s%N)

for i in {1..1000}; do
  curl -s -X POST http://localhost:8000/api/entities \
    -H "Content-Type: application/json" \
    -d "{
      \"type\": \"Person\",
      \"name\": \"Person $i\",
      \"properties\": {\"index\": $i}
    }" > /dev/null
done

END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))

echo "Created 1000 entities in ${DURATION}ms"
echo "Average: $((DURATION / 1000))ms per entity"
```

**Success Criteria:**
- All 1000 entities created
- Average response time < 100ms
- No errors
- Database responsive

### Test 20: Query Performance

**Objective:** Measure search and path-finding performance

```bash
#!/bin/bash

echo "Testing search performance..."
START=$(date +%s%N)

for i in {1..100}; do
  curl -s -X GET "http://localhost:8000/api/search?q=Person" > /dev/null
done

END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))

echo "100 searches in ${DURATION}ms"
echo "Average: $((DURATION / 100))ms per search"
```

**Success Criteria:**
- Average search time < 50ms
- Consistent performance
- No timeouts
- Results accurate

---

## ✅ Test Execution Checklist

- [ ] Test 1: Health Check
- [ ] Test 2: Documentation
- [ ] Test 3: Create Entity
- [ ] Test 4: Get Entity
- [ ] Test 5: List Entities
- [ ] Test 6: Update Entity
- [ ] Test 7: Delete Entity
- [ ] Test 8: Create Relationship
- [ ] Test 9: Find Path
- [ ] Test 10: Related Entities
- [ ] Test 11: Full-Text Search
- [ ] Test 12: Advanced Search
- [ ] Test 13: Ask Question
- [ ] Test 14: Q&A History
- [ ] Test 15: Graph Data
- [ ] Test 16: System Status
- [ ] Test 17: System Metrics
- [ ] Test 18: Integration Workflow
- [ ] Test 19: Bulk Creation
- [ ] Test 20: Query Performance

---

## 📊 Test Results Summary

**Date:** [To be filled in]
**Tester:** [To be filled in]
**Environment:** [Docker/Local/Cloud]

| Test | Status | Duration | Notes |
|------|--------|----------|-------|
| 1 | ✅ | - | - |
| 2 | ✅ | - | - |
| 3 | ✅ | - | - |
| ... | | | |

**Overall Result:** ✅ PASS / ❌ FAIL

---

**Last Updated:** December 17, 2025
**Next Review:** After launch

Built with ❤️ by Nathan Poinsette
