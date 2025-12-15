# Sherlock Hub - System Architecture

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Part of:** Echo Hybrid Intelligence Ecosystem

---

## 🏗️ Architecture Overview

Sherlock Hub is built on a **multi-tier, microservices architecture** designed for scalability, resilience, and constitutional AI compliance.

### Core Principles

1. **Evidence-Based Intelligence** - All data classified by credibility
2. **Constitutional AI** - Ethical safeguards at every layer
3. **Graph-First Design** - Relationships are first-class citizens
4. **Auto-Discovery** - Services find and connect automatically
5. **Echo Preservation** - Complete audit trail of all operations

---

## 📊 System Layers

```
┌─────────────────────────────────────────────────────┐
│              PRESENTATION LAYER                      │
│  React Frontend + Cytoscape Graph Visualization     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              APPLICATION LAYER                       │
│  FastAPI REST API + Constitutional AI Middleware    │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              COORDINATION LAYER                      │
│  Nexus Coordinator + Service Discovery + Echo Log   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              DATA LAYER                              │
│  Neo4j Graph Database + Redis Cache                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              INGESTION LAYER                         │
│  Apache Airflow ETL + Data Validation               │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Component Details

### 1. Frontend (React + Cytoscape)

**Purpose:** Interactive graph visualization and user interface

**Key Features:**
- Real-time graph rendering with Cytoscape.js
- Evidence tier color coding (Green/Yellow/Red)
- Search and filtering
- AI-powered Q&A interface
- Responsive design for all devices

**Technology Stack:**
- React 18 (concurrent features)
- Cytoscape.js (graph visualization)
- Tailwind CSS (styling)
- Vite (build tool)
- Axios (API client)

**File Structure:**
```
frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Page-level components
│   ├── lib/           # API client and utilities
│   └── styles/        # CSS and Tailwind config
├── public/            # Static assets
└── package.json       # Dependencies
```

---

### 2. Backend API (FastAPI)

**Purpose:** RESTful API with constitutional AI safeguards

**Key Features:**
- Automatic OpenAPI documentation
- JWT authentication
- Rate limiting
- CORS support
- Constitutional AI middleware

**API Endpoints:**

**Entities API** (`/api/entities`)
- `GET /` - List all entities
- `GET /{id}` - Get entity details
- `POST /` - Create entity (admin only)
- `PUT /{id}` - Update entity
- `DELETE /{id}` - Delete entity

**Paths API** (`/api/paths`)
- `GET /find` - Find shortest path between entities
- `GET /explore` - Explore connections up to N degrees

**Q&A API** (`/api/qa`)
- `POST /ask` - Ask question with LLM + constitutional safeguards
- `GET /history` - Get conversation history

**Search API** (`/api/search`)
- `GET /` - Full-text search across entities
- `GET /filter` - Advanced filtering

**Documents API** (`/api/documents`)
- `GET /` - List source documents
- `GET /{id}` - Get document details
- `POST /` - Upload new document

**Nexus API** (`/api/nexus`)
- `GET /services` - List registered services
- `GET /health` - System health check
- `GET /echo` - Echo log entries

**Technology Stack:**
- FastAPI (async Python web framework)
- Pydantic (data validation)
- Neo4j Python Driver
- OpenAI Python SDK
- Python-JOSE (JWT)

---

### 3. Nexus Coordinator

**Purpose:** Service discovery, coordination, and echo preservation

**Key Features:**
- **Auto-Discovery:** Services register capabilities on startup
- **Handshake Protocol:** Services negotiate connections
- **Echo Logging:** Immutable audit trail
- **Health Monitoring:** Track service status
- **Message Bus:** Inter-service communication

**Service Registration:**
```python
{
  "service_id": "entity-api",
  "capabilities": ["entity_crud", "graph_query"],
  "endpoints": ["/api/entities"],
  "status": "healthy",
  "registered_at": "2025-12-15T10:00:00Z"
}
```

**Echo Log Entry:**
```python
{
  "timestamp": "2025-12-15T10:00:00Z",
  "event": "entity_created",
  "service": "entity-api",
  "details": {"entity_id": "E123", "type": "Person"},
  "user": "admin@example.com"
}
```

---

### 4. Graph Database (Neo4j)

**Purpose:** Store entities and relationships with evidence tiers

**Schema:**

**Nodes:**
- `Person` - Individual entities
- `Organization` - Companies, institutions
- `Location` - Geographic locations
- `Event` - Temporal occurrences
- `Document` - Source materials

**Relationships:**
- `CONNECTED_TO` - Generic connection
- `EMPLOYED_BY` - Employment relationship
- `LOCATED_AT` - Geographic association
- `ATTENDED` - Event participation
- `MENTIONED_IN` - Document reference

**Properties:**
- `evidence_tier` - Documented/Reported/Alleged
- `source_ids` - Array of source document IDs
- `confidence_score` - 0.0 to 1.0
- `created_at` - Timestamp
- `updated_at` - Timestamp

**Indexes:**
```cypher
CREATE INDEX entity_name FOR (n:Person) ON (n.name);
CREATE INDEX entity_type FOR (n) ON (n.type);
CREATE FULLTEXT INDEX entity_search FOR (n:Person|Organization) ON EACH [n.name, n.description];
```

---

### 5. ETL Pipelines (Apache Airflow)

**Purpose:** Automated data ingestion from multiple sources

**Data Sources:**
- Court documents (PDF parsing)
- Flight records (CSV/API)
- Property records (public databases)
- Corporate filings (SEC EDGAR)
- News articles (web scraping)

**Pipeline Stages:**
1. **Extract:** Pull raw data from sources
2. **Transform:** Parse, clean, validate
3. **Entity Extraction:** Identify entities and relationships
4. **Evidence Classification:** Assign tier based on source
5. **Load:** Insert into Neo4j with proper schema

**Airflow DAG:**
```python
data_ingestion_dag = DAG(
    'sherlock_hub_ingestion',
    schedule_interval='@daily',
    default_args={'retries': 3}
)

extract_task >> transform_task >> load_task
```

---

## 🔐 Security Architecture

### Authentication & Authorization

**JWT-Based Authentication:**
- Access tokens (15 min expiry)
- Refresh tokens (7 day expiry)
- Role-based access control (RBAC)

**Roles:**
- `viewer` - Read-only access
- `analyst` - Read + search + Q&A
- `editor` - Analyst + create/update entities
- `admin` - Full access

### Data Protection

**Encryption:**
- TLS 1.3 for all API traffic
- AES-256 for data at rest
- Encrypted backups

**Privacy:**
- PII redaction in logs
- Victim identity masking
- GDPR/CCPA compliance

---

## 🌐 Integration with Echo Ecosystem

### Global Nexus Integration

Sherlock Hub registers with the Echo Global Nexus:
```python
{
  "component": "sherlock-hub",
  "capabilities": [
    "graph_intelligence",
    "entity_mapping",
    "evidence_analysis"
  ],
  "endpoints": {
    "api": "http://sherlock-hub:8000",
    "nexus": "http://sherlock-hub:8000/api/nexus"
  }
}
```

### Data Sharing

- Entities can be shared with other Echo components
- Graph queries accessible via Global Cortex
- Echo logs synchronized across ecosystem

---

## 📈 Scalability & Performance

### Horizontal Scaling

**Backend API:**
- Stateless design
- Load balanced across multiple instances
- Auto-scaling based on CPU/memory

**Neo4j:**
- Causal clustering (3+ nodes)
- Read replicas for queries
- Write master for updates

### Caching Strategy

**Redis Cache:**
- Frequently accessed entities (TTL: 5 min)
- Search results (TTL: 1 min)
- API responses (TTL: 30 sec)

### Performance Targets

- API response time: < 100ms (p95)
- Graph query: < 500ms (p95)
- Search: < 200ms (p95)
- Concurrent users: 1000+

---

## 🔄 Deployment Architecture

### Development Environment

```bash
docker-compose up -d
# Neo4j + Backend + Frontend + Redis
```

### Production Environment

**Kubernetes Deployment:**
- 3 backend pods (auto-scaling)
- 3 Neo4j nodes (causal cluster)
- 1 Redis pod
- 1 Airflow scheduler + 3 workers
- Ingress controller (NGINX)

**Monitoring:**
- Prometheus (metrics)
- Grafana (dashboards)
- ELK Stack (logs)

---

## 🎯 Future Enhancements

1. **Real-time Updates:** WebSocket for live graph changes
2. **ML-Powered Insights:** Pattern detection and anomaly identification
3. **Multi-tenancy:** Isolated environments for different organizations
4. **Advanced Visualization:** 3D graph rendering, timeline view
5. **Mobile App:** Native iOS/Android applications

---

## 📚 Related Documentation

- [Technical Specification](TECHNICAL_SPECIFICATION.md)
- [API Documentation](http://localhost:8000/docs)
- [Echo Log Philosophy](ECHO_LOG.md)
- [Deployment Guide](../README.md)

---

**Built with ❤️ as part of the Echo Hybrid Intelligence Ecosystem**

