# Contributing to Sherlock Hub

Thank you for your interest in contributing to Sherlock Hub! This document provides guidelines and best practices for contributing to the project.

---

## 🎯 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, identity, or experience level.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

---

## 🚀 Getting Started

### 1. Fork the Repository

```bash
gh repo fork onlyecho822-source/Echo
cd Echo/sherlock-hub
```

### 2. Set Up Development Environment

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Start services
cd ..
docker-compose up -d
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## 📝 Contribution Types

### 1. Bug Fixes

**Before submitting:**
- Check if the bug is already reported in Issues
- Verify the bug exists in the latest version
- Include steps to reproduce

**Pull Request Requirements:**
- Clear description of the bug
- Steps to reproduce
- Your fix and why it works
- Tests that verify the fix

### 2. New Features

**Before starting:**
- Open an Issue to discuss the feature
- Get feedback from maintainers
- Ensure it aligns with project goals

**Pull Request Requirements:**
- Feature description and use case
- Implementation details
- Tests for new functionality
- Documentation updates

### 3. Documentation

**Always welcome:**
- Fixing typos or unclear explanations
- Adding examples
- Improving API documentation
- Translating documentation

### 4. Tests

**Highly valued:**
- Adding missing test coverage
- Improving existing tests
- Adding integration tests
- Performance benchmarks

---

## 💻 Development Guidelines

### Code Style

**Python (Backend):**
```python
# Use Black for formatting
black backend/

# Use isort for imports
isort backend/

# Use flake8 for linting
flake8 backend/

# Type hints required
def create_entity(name: str, entity_type: str) -> Entity:
    pass
```

**JavaScript/React (Frontend):**
```javascript
// Use Prettier for formatting
npm run format

// Use ESLint for linting
npm run lint

// Functional components with hooks
const MyComponent = () => {
  const [state, setState] = useState(null)
  return <div>{state}</div>
}
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add entity export functionality
fix: resolve graph rendering issue on mobile
docs: update API documentation for search endpoint
test: add integration tests for Q&A API
refactor: simplify database connection logic
```

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Tests
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `chore` - Maintenance

### Testing Requirements

**All PRs must include tests:**

**Backend Tests:**
```python
# backend/tests/test_entities.py
import pytest
from api.routes import entities

def test_create_entity():
    response = client.post("/api/entities", json={
        "name": "Test Entity",
        "type": "Person"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Test Entity"
```

**Frontend Tests:**
```javascript
// frontend/src/__tests__/App.test.jsx
import { render, screen } from '@testing-library/react'
import App from '../App'

test('renders Sherlock Hub title', () => {
  render(<App />)
  expect(screen.getByText(/Sherlock Hub/i)).toBeInTheDocument()
})
```

**Run tests before submitting:**
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

---

## 🔍 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### 2. PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes
```

### 3. Review Process

- Maintainers will review within 48 hours
- Address feedback promptly
- Keep discussions respectful
- Be open to suggestions

### 4. Merging

- Requires 1 approval from maintainer
- All tests must pass
- No merge conflicts
- Squash and merge preferred

---

## 🏗️ Architecture Decisions

### Adding New API Endpoints

1. Create route in `backend/api/routes/`
2. Add to router in `backend/api/main.py`
3. Update OpenAPI documentation
4. Add tests in `backend/tests/`

### Adding New Frontend Pages

1. Create component in `frontend/src/pages/`
2. Add route in `frontend/src/App.jsx`
3. Update navigation
4. Add tests in `frontend/src/__tests__/`

### Database Schema Changes

1. Create migration script
2. Update Neo4j schema documentation
3. Test with sample data
4. Document in ARCHITECTURE.md

---

## 🎨 Design Guidelines

### UI/UX Principles

1. **Evidence-First:** Always show evidence tier
2. **Clarity:** Avoid jargon, use plain language
3. **Accessibility:** WCAG 2.1 AA compliance
4. **Responsiveness:** Mobile-first design

### Color Palette

```css
/* Evidence Tiers */
--documented: #10b981;  /* Green */
--reported: #f59e0b;    /* Yellow */
--alleged: #ef4444;     /* Red */

/* UI Colors */
--primary: #3b82f6;     /* Blue */
--secondary: #6366f1;   /* Indigo */
--background: #f9fafb;  /* Light gray */
--text: #111827;        /* Dark gray */
```

---

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. macOS 14.0]
- Browser: [e.g. Chrome 120]
- Version: [e.g. 1.0.0]

**Additional context**
Any other relevant information.
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Mockups, examples, or references.
```

---

## 📚 Resources

### Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Echo Log Philosophy](docs/ECHO_LOG.md)

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cytoscape.js Documentation](https://js.cytoscape.org/)

---

## 🙏 Recognition

Contributors are recognized in:
- README.md Contributors section
- Release notes
- Project website (when available)

---

## 📞 Getting Help

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and ideas
- **Email:** [Your contact email]

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

**Thank you for contributing to Sherlock Hub!**

*Part of the Echo Hybrid Intelligence Ecosystem*

