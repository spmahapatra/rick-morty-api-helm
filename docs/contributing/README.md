# Contributing and Development Documentation

This directory contains guidelines for contributing to the project, development setup, and best practices.

## Contents

### Getting Started
📄 **[`DEVELOPMENT_SETUP.md`](DEVELOPMENT_SETUP.md)**
- Local development environment setup
- Docker Compose setup
- Project structure overview
- Common development tasks
- Debugging techniques

### Contribution Guidelines
📄 **[`CONTRIBUTING.md`](CONTRIBUTING.md)**
- How to contribute to the project
- Bug reporting and feature requests
- Contribution workflow
- Commit guidelines
- Code review process

### Code Standards
📄 **[`CODE_STANDARDS.md`](CODE_STANDARDS.md)**
- Python style guide and best practices
- Naming conventions
- Code organization
- Documentation standards
- Testing requirements
- Security best practices

### Testing Guide
📄 **[`TESTING_GUIDE.md`](TESTING_GUIDE.md)** *(Coming Soon)*
- Testing strategies
- Unit test examples
- Integration testing
- Test coverage requirements
- Mock and fixture usage

### Git Workflow
📄 **[`GIT_WORKFLOW.md`](GIT_WORKFLOW.md)** *(Coming Soon)*
- Git branching strategy
- Pull request procedures
- Commit message guidelines
- Merge and rebase strategies
- Conflict resolution

---

## Quick Links

| Need | Document |
|------|----------|
| Setup development | `DEVELOPMENT_SETUP.md` |
| Contribute code | `CONTRIBUTING.md` |
| Code standards | `CODE_STANDARDS.md` |
| Write tests | `TESTING_GUIDE.md` |
| Git procedures | `GIT_WORKFLOW.md` |

---

## Contribution Workflow

1. **Setup Environment** → `DEVELOPMENT_SETUP.md`
2. **Understand Standards** → `CODE_STANDARDS.md`
3. **Make Changes** → Follow contribution guidelines
4. **Write Tests** → `TESTING_GUIDE.md`
5. **Commit Changes** → `GIT_WORKFLOW.md`
6. **Submit PR** → `CONTRIBUTING.md`

---

## Quick Start for Contributors

### 1. Setup Development Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
docker-compose up -d
```

### 2. Run Tests
```bash
pytest tests/ -v --cov=src
```

### 3. Check Code Quality
```bash
flake8 src/
mypy src/
black src/
```

### 4. Create Feature Branch
```bash
git checkout -b feature/your-feature
```

### 5. Commit with Proper Message
```bash
git commit -m "feat(scope): clear description"
```

### 6. Push and Create PR
```bash
git push origin feature/your-feature
# Create PR on GitHub
```

---

## Development Standards Summary

✅ **Must Do**
- Write tests for new features
- Follow Black formatting: `black src/`
- Type hints on public functions
- Docstrings on all public APIs
- No hardcoded secrets
- Update relevant documentation

❌ **Must Not Do**
- Commit without passing tests
- Mix formatting and logic changes
- Leave TODO comments without addressing
- Add dependencies without justification
- Log sensitive information

---

## Code Quality Tools

| Tool | Purpose | Command |
|------|---------|---------|
| Black | Code formatting | `black src/ tests/` |
| Flake8 | Style checking | `flake8 src/ tests/` |
| MyPy | Type checking | `mypy src/` |
| Pytest | Unit testing | `pytest tests/` |
| Bandit | Security scanning | `bandit -r src/` |

---

## Related Documentation

- **Architecture**: See [`docs/architecture/`](../architecture/) for system design
- **API**: See [`docs/api/`](../api/) for endpoint reference
- **Deployment**: See [`docs/deployment/`](../deployment/) for production setup
- **Examples**: See [`docs/examples/`](../examples/) for code samples

---

## In This Directory

```
contributing/
├── README.md (this file)
├── DEVELOPMENT_SETUP.md
├── CONTRIBUTING.md
├── CODE_STANDARDS.md
├── TESTING_GUIDE.md (coming soon)
└── GIT_WORKFLOW.md (coming soon)
```

## Status

| Document | Status |
|----------|--------|
| DEVELOPMENT_SETUP | ✅ Complete |
| CONTRIBUTING | ✅ Complete |
| CODE_STANDARDS | ✅ Complete |
| TESTING_GUIDE | 🟡 Planned |
| GIT_WORKFLOW | 🟡 Planned |

---

## Questions?

- Check `DEVELOPMENT_SETUP.md` for environment setup issues
- Review `CODE_STANDARDS.md` for coding guidelines
- See `CONTRIBUTING.md` for contribution procedures
