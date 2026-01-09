# 📞 Support Guide

Welcome to Sherlock Hub support! We're here to help you get the most out of our platform.

---

## 🚀 Getting Started

### First Steps
1. **Read the README** - Start with [README_LAUNCH.md](./README_LAUNCH.md) for basic setup
2. **Watch tutorials** - Video guides coming soon
3. **Explore the API** - Visit http://localhost:8000/docs for interactive documentation
4. **Check the docs** - See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for deep dives

### Quick Links
- **GitHub Repository:** https://github.com/onlyecho822-source/Echo
- **Issue Tracker:** https://github.com/onlyecho822-source/Echo/issues
- **Discussions:** https://github.com/onlyecho822-source/Echo/discussions
- **API Docs:** http://localhost:8000/docs (when running)

---

## 💬 Getting Help

### 1. Self-Service Resources

**Documentation**
- [README_LAUNCH.md](./README_LAUNCH.md) - Setup and usage
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System design
- [ROADMAP.md](./ROADMAP.md) - Future features
- [SECURITY.md](./SECURITY.md) - Security policies
- [CONTRIBUTING.md](./CONTRIBUTING.md) - How to contribute

**API Documentation**
- Interactive Swagger UI: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

**Video Tutorials**
- Coming soon on YouTube
- Subscribe to be notified

### 2. Community Support

**GitHub Discussions**
Ask questions and connect with other users:
https://github.com/onlyecho822-source/Echo/discussions

**Response Time:** Best effort, typically 24-48 hours

**How to ask a good question:**
1. Search existing discussions first
2. Provide clear description of your issue
3. Include relevant error messages
4. Share your environment (OS, Docker version, etc.)
5. Be patient and respectful

### 3. Bug Reports

**Found a bug?** Please report it on GitHub:
https://github.com/onlyecho822-source/Echo/issues

**Include in your report:**
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs
- Your environment (OS, Docker version, etc.)
- Screenshots if applicable

**Response Time:** Critical bugs within 24 hours, others within 48-72 hours

### 4. Feature Requests

**Have an idea?** We'd love to hear it!

**Where to request:**
- GitHub Discussions: https://github.com/onlyecho822-source/Echo/discussions
- Feature voting: https://github.com/onlyecho822-source/Echo/discussions/categories/feature-requests
- Email: feedback@nathanpoinsette.com

**What makes a good feature request:**
1. Clear description of the feature
2. Why you need it (use case)
3. How it would benefit others
4. Mockups or examples if applicable

### 5. Email Support

**General inquiries:** support@nathanpoinsette.com
**Response Time:** Within 48 hours

**Security issues:** security@nathanpoinsette.com
**Response Time:** Within 24 hours (urgent)

**Enterprise support:** enterprise@nathanpoinsette.com
**Response Time:** Within 4 hours (SLA available)

---

## 🔧 Troubleshooting

### Common Issues & Solutions

**Issue: "Connection refused" error**

**Cause:** Services not running or not ready

**Solution:**
```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs backend

# Restart services
docker-compose restart

# Wait 30 seconds for services to be ready
sleep 30
```

**Issue: "Port already in use"**

**Cause:** Another process is using the port

**Solution:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
docker-compose -p myproject up
```

**Issue: "Neo4j authentication failed"**

**Cause:** Incorrect password or Neo4j not initialized

**Solution:**
```bash
# Check Neo4j logs
docker logs sherlock-hub-neo4j

# Reset Neo4j (warning: deletes data)
docker-compose down
docker volume rm sherlock-hub_neo4j_data
docker-compose up
```

**Issue: "Out of memory" errors**

**Cause:** Not enough RAM allocated to Docker

**Solution:**
```bash
# Increase Docker memory limit
# Edit docker-compose.yml:
services:
  backend:
    mem_limit: 2g
  neo4j:
    mem_limit: 2g

# Restart
docker-compose down
docker-compose up
```

**Issue: "API returns 500 error"**

**Cause:** Backend error

**Solution:**
```bash
# Check backend logs
docker logs sherlock-hub-backend

# Check for specific error
docker logs sherlock-hub-backend | grep ERROR

# Restart backend
docker-compose restart backend
```

**Issue: "Frontend not loading"**

**Cause:** Frontend build error or connection issue

**Solution:**
```bash
# Check frontend logs
docker logs sherlock-hub-frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up frontend

# Clear browser cache (Ctrl+Shift+Del)
```

---

## 📊 Performance Troubleshooting

### Slow Queries

**Symptoms:** API responses taking >5 seconds

**Diagnosis:**
```bash
# Check Neo4j query logs
docker exec sherlock-hub-neo4j cypher-shell -u neo4j -p password \
  "CALL dbms.queryJmx('*') YIELD query, elapsedTimeMs RETURN query, elapsedTimeMs ORDER BY elapsedTimeMs DESC LIMIT 10"
```

**Solutions:**
1. Add database indexes
2. Optimize query patterns
3. Increase Neo4j memory
4. Clear cache: `docker-compose restart redis`

### High CPU Usage

**Symptoms:** CPU constantly at 100%

**Diagnosis:**
```bash
# Check which container is using CPU
docker stats

# Check logs for errors
docker logs sherlock-hub-backend
```

**Solutions:**
1. Reduce concurrent requests
2. Optimize data processing
3. Scale horizontally with multiple instances
4. Check for infinite loops in custom code

### High Memory Usage

**Symptoms:** Memory usage growing over time

**Diagnosis:**
```bash
# Check memory usage
docker stats

# Check for memory leaks
docker logs sherlock-hub-backend | grep -i memory
```

**Solutions:**
1. Restart services: `docker-compose restart`
2. Increase allocated memory
3. Optimize data structures
4. Enable garbage collection

---

## 🔐 Security Issues

### Reporting Security Vulnerabilities

**Do NOT create a public GitHub issue for security issues.**

**Instead, email:** security@nathanpoinsette.com

**Include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

**Response Timeline:**
- **Initial Response:** Within 24 hours
- **Fix Development:** Within 7 days
- **Public Disclosure:** After fix is released (typically 30 days)

### Security Best Practices

1. **Keep dependencies updated**
   ```bash
   npm audit fix
   pip install --upgrade -r requirements.txt
   ```

2. **Use strong passwords**
   - Neo4j: Change default password immediately
   - API: Use JWT tokens with strong secrets

3. **Enable HTTPS in production**
   - Use SSL certificates
   - Configure CORS properly
   - Set secure headers

4. **Monitor access logs**
   - Review authentication failures
   - Monitor API usage
   - Set up alerts

---

## 📈 Monitoring & Health Checks

### System Health

**Check if services are running:**
```bash
docker-compose ps
```

**View real-time metrics:**
```bash
docker stats
```

**Check logs:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend

# Follow logs (live)
docker-compose logs -f backend
```

### Health Endpoints

**Backend health:**
```bash
curl http://localhost:8000/health
```

**Database health:**
```bash
docker exec sherlock-hub-neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

**Frontend health:**
```bash
curl http://localhost:3000
```

---

## 🎓 Learning Resources

### Documentation
- [Architecture Guide](./docs/ARCHITECTURE.md) - System design and components
- [API Reference](http://localhost:8000/docs) - Interactive API documentation
- [Echo Log System](./docs/ECHO_LOG.md) - Journey preservation and logging

### Video Tutorials
- Coming soon on YouTube
- Subscribe to be notified

### Blog Posts
- Coming soon on our website

### Community Examples
- Share your use cases in GitHub Discussions
- See what others are building

---

## 💼 Enterprise Support

### Professional Support Tiers

**Starter Support**
- Email support
- Response time: 48 hours
- Cost: Free

**Professional Support**
- Email + chat support
- Response time: 24 hours
- Priority issue handling
- Monthly check-ins
- Cost: $500/month

**Enterprise Support**
- 24/7 phone + email support
- Response time: 4 hours
- Dedicated account manager
- Custom SLA
- Priority feature development
- Cost: Custom pricing

### Enterprise Inquiries

Contact: enterprise@nathanpoinsette.com

**Include in your inquiry:**
- Company name and size
- Current use case
- Expected scale
- Support requirements
- Timeline

---

## 🤝 Contributing

Want to help improve Sherlock Hub?

**Ways to contribute:**
1. Report bugs
2. Suggest features
3. Improve documentation
4. Submit code changes
5. Share your use cases

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

---

## 📞 Contact Information

| Channel | Purpose | Response Time |
|---------|---------|----------------|
| **GitHub Issues** | Bug reports | 24-72 hours |
| **GitHub Discussions** | Questions & ideas | 24-48 hours |
| **Email (support@)** | General support | 48 hours |
| **Email (security@)** | Security issues | 24 hours |
| **Email (enterprise@)** | Enterprise support | 4 hours |
| **Email (feedback@)** | Feature requests | 48 hours |

---

## 📋 FAQ

**Q: Is Sherlock Hub free?**
A: Yes! Sherlock Hub is open source and free to use. Enterprise support is available for a fee.

**Q: Can I use Sherlock Hub in production?**
A: Yes. Version 1.0.0 is production-ready. See [SECURITY.md](./SECURITY.md) for security considerations.

**Q: How do I update to new versions?**
A: Pull the latest code and run `docker-compose up --build`.

**Q: Can I contribute to Sherlock Hub?**
A: Absolutely! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Q: How do I report a security vulnerability?**
A: Email security@nathanpoinsette.com with details.

**Q: Is there a commercial version?**
A: Enterprise support and custom features are available. Contact enterprise@nathanpoinsette.com.

---

## 🎯 What's Next?

1. **Read the documentation** - Start with [README_LAUNCH.md](./README_LAUNCH.md)
2. **Launch the platform** - Run `docker-compose up`
3. **Explore the API** - Visit http://localhost:8000/docs
4. **Join the community** - GitHub Discussions
5. **Share feedback** - Help us improve!

---

**Last Updated:** December 17, 2025

**Built with ❤️ by Nathan Poinsette**
Veteran-owned. Open Source. Always.
