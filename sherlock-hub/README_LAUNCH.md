# 🔍 Sherlock Hub - Intelligence Platform

**Graph-based entity mapping, relationship discovery, and intelligent analysis platform.**

Built by **Nathan Poinsette** | Veteran-owned | Open Source | MIT License

---

## 🎯 What is Sherlock Hub?

Sherlock Hub is an advanced intelligence platform that maps complex relationships between entities and discovers hidden patterns in data. It combines graph databases, natural language processing, and interactive visualization to help you understand your data at a deeper level.

**Key Capabilities:**
- 🔗 **Entity Mapping** - Visualize relationships between entities in an interactive graph
- 🔍 **Intelligent Search** - Full-text search with semantic understanding
- 💬 **Natural Language Q&A** - Ask questions about your data in plain English
- 📊 **Graph Visualization** - Beautiful, interactive Cytoscape.js visualizations
- 🔄 **ETL Pipelines** - Apache Airflow integration for data processing
- 🌐 **RESTful API** - Comprehensive API for programmatic access

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 4GB RAM minimum
- 2GB disk space

### Launch in 30 Seconds

```bash
# Clone the repository
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo/sherlock-hub

# Start all services
docker-compose up

# Wait for "Application startup complete" message
```

**Services will be available at:**
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Neo4j Browser:** http://localhost:7474

---

## 📖 Usage

### 1. Dashboard
Visit http://localhost:3000 to access the main dashboard.

**Features:**
- System overview and statistics
- Quick access to all modules
- Recent activity feed
- Search bar for quick entity lookup

### 2. Graph Explorer
Visualize and explore entity relationships.

**How to use:**
1. Click "Graph Explorer" in the navigation
2. Select an entity type to start
3. Click nodes to expand relationships
4. Drag to pan, scroll to zoom
5. Click on relationships to see details

### 3. Search
Full-text search across all entities.

**How to use:**
1. Click "Search" in the navigation
2. Enter a search term
3. Filter by entity type
4. Click results to view details

### 4. Q&A
Ask natural language questions about your data.

**How to use:**
1. Click "Q&A" in the navigation
2. Type a question (e.g., "What entities are connected to Person X?")
3. Review the AI-generated answer
4. Click linked entities to explore further

### 5. Entity Profiles
View detailed information about any entity.

**Features:**
- Complete entity information
- Related entities
- Relationship history
- Document references

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# API
API_HOST=0.0.0.0
API_PORT=8000
API_LOG_LEVEL=INFO

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_LOG_LEVEL=info

# OpenAI (for Q&A features)
OPENAI_API_KEY=your_api_key_here

# Redis (optional, for caching)
REDIS_URL=redis://redis:6379
```

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  neo4j:
    environment:
      NEO4J_AUTH: neo4j/your_password
      NEO4J_PLUGINS: '["apoc"]'

  backend:
    environment:
      NEO4J_PASSWORD: your_password
      OPENAI_API_KEY: your_api_key

  frontend:
    environment:
      REACT_APP_API_URL: http://localhost:8000
```

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 18 + TypeScript | User interface |
| **Backend** | FastAPI (Python) | REST API |
| **Database** | Neo4j 5.x | Graph database |
| **Visualization** | Cytoscape.js | Graph rendering |
| **Styling** | Tailwind CSS | UI styling |
| **ETL** | Apache Airflow | Data pipelines |
| **Caching** | Redis | Performance |
| **Container** | Docker | Deployment |

### System Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend (React)              │
│  Dashboard | Explorer | Search | Q&A | Profiles│
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│                Backend (FastAPI)                │
│  /entities | /paths | /search | /qa | /nexus   │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Neo4j  │  │ Redis  │  │Airflow │
    │ Graph  │  │ Cache  │  │ ETL    │
    │Database│  │        │  │ Pipes  │
    └────────┘  └────────┘  └────────┘
```

---

## 📚 API Documentation

### Interactive API Docs
Visit http://localhost:8000/docs for interactive Swagger documentation.

### Key Endpoints

**Entities**
```bash
GET    /api/entities              # List all entities
GET    /api/entities/{id}         # Get entity details
POST   /api/entities              # Create entity
PUT    /api/entities/{id}         # Update entity
DELETE /api/entities/{id}         # Delete entity
```

**Relationships**
```bash
GET    /api/paths/{from}/{to}     # Find paths between entities
GET    /api/entities/{id}/related # Get related entities
POST   /api/relationships         # Create relationship
```

**Search**
```bash
GET    /api/search?q=term         # Full-text search
GET    /api/search/advanced       # Advanced search
```

**Q&A**
```bash
POST   /api/qa                    # Ask a question
GET    /api/qa/{id}               # Get Q&A history
```

### Example Requests

**Create an Entity:**
```bash
curl -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Person",
    "name": "John Doe",
    "properties": {
      "email": "john@example.com",
      "role": "Engineer"
    }
  }'
```

**Search for Entities:**
```bash
curl http://localhost:8000/api/search?q=john
```

**Ask a Question:**
```bash
curl -X POST http://localhost:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What entities are connected to John Doe?"
  }'
```

---

## 🔐 Security

### Security Features
- ✅ No hardcoded secrets
- ✅ Environment variable configuration
- ✅ HTTPS-ready (configure in production)
- ✅ Input validation on all endpoints
- ✅ SQL injection protection
- ✅ CORS configuration available

### Production Deployment

For production, ensure:

1. **Use HTTPS:**
   ```bash
   # Configure in docker-compose.yml
   HTTPS_ENABLED=true
   SSL_CERT_PATH=/path/to/cert.pem
   ```

2. **Set strong passwords:**
   ```bash
   NEO4J_PASSWORD=your_very_secure_password_here
   ```

3. **Enable authentication:**
   ```bash
   API_AUTH_ENABLED=true
   JWT_SECRET=your_jwt_secret_key
   ```

4. **Configure CORS:**
   ```bash
   CORS_ORIGINS=https://yourdomain.com
   ```

See [SECURITY.md](./SECURITY.md) for detailed security policies.

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/onlyecho822-source/Echo.git
cd Echo/sherlock-hub

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start development servers
npm run dev  # Frontend (port 3000)
# In another terminal:
cd ../backend
python -m uvicorn api.main:app --reload  # Backend (port 8000)
```

### Running Tests

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# With coverage
pytest --cov=api tests/
```

### Code Quality

```bash
# Lint frontend
cd frontend
npm run lint

# Format code
npm run format

# Backend linting
cd backend
pylint api/
black api/
```

---

## 📊 Data Import

### Using ETL Pipelines

Sherlock Hub includes Apache Airflow for data processing:

```bash
# Access Airflow UI
http://localhost:8080

# Trigger a DAG
airflow dags trigger data_ingestion_dag
```

### Manual Data Import

```bash
# Via API
curl -X POST http://localhost:8000/api/entities \
  -H "Content-Type: application/json" \
  -d @entities.json

# Via Neo4j
docker exec sherlock-hub-neo4j neo4j-admin import \
  --nodes=entities.csv \
  --relationships=relationships.csv
```

---

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find and kill process using port 3000
lsof -i :3000
kill -9 <PID>

# Or use different port
docker-compose up -p custom_port
```

**Neo4j Connection Error**
```bash
# Check Neo4j logs
docker logs sherlock-hub-neo4j

# Verify connection
docker exec sherlock-hub-neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

**Out of Memory**
```bash
# Increase Docker memory
# Edit docker-compose.yml:
services:
  backend:
    mem_limit: 2g
  neo4j:
    mem_limit: 2g
```

**API Not Responding**
```bash
# Check backend logs
docker logs sherlock-hub-backend

# Restart services
docker-compose restart backend
```

---

## 📈 Performance Optimization

### Caching
- Redis caching enabled by default
- Configure cache TTL in `.env`
- Monitor cache hit rates in logs

### Database Optimization
- Neo4j indexes created automatically
- Query optimization in place
- Connection pooling configured

### Frontend Optimization
- Code splitting enabled
- Lazy loading for components
- Image optimization
- CSS minification

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📞 Support

**Documentation:**
- [Architecture Guide](./docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Echo Log System](./docs/ECHO_LOG.md)

**Getting Help:**
- GitHub Issues: https://github.com/onlyecho822-source/Echo/issues
- GitHub Discussions: https://github.com/onlyecho822-source/Echo/discussions
- Email: support@nathanpoinsette.com

**Security Issues:**
- Email: security@nathanpoinsette.com

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- **FastAPI** - Modern Python web framework
- **React 18** - UI library
- **Neo4j** - Graph database
- **Cytoscape.js** - Graph visualization
- **Tailwind CSS** - Styling
- **Apache Airflow** - Workflow orchestration

---

**Built with ❤️ by Nathan Poinsette**
Veteran-owned. Open Source. Always.

Last Updated: December 17, 2025
