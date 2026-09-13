# Documentation Index

This directory contains all project documentation, organized by type and purpose.

## Structure

```
docs/
├── README.md (this file)
└── dev-notes/          # Development-time notes (see .gitignore)
    ├── README.md       # Index of development notes
    ├── analysis/       # Development analysis & summaries
    ├── cache-docs/     # Cache feature reference docs
    ├── debugging/      # Troubleshooting guides
    ├── logging-docs/   # Logging implementation reference
    └── process-docs/   # Process & policy documentation
```

## Documentation Categories

### Essential Project Documentation (Root Level)
Located in the project root directory:

1. **README.md** - Main project overview and getting started guide
2. **DEPLOYMENT_VALIDATION_REPORT.md** - Comprehensive validation results and production readiness assessment
3. **PRE_DOCKER_AUDIT_REPORT.md** - Critical issues identified and how they were fixed
4. **POSTGRESQL_HEALTHCHECK_FIX.md** - PostgreSQL configuration and health check troubleshooting
5. **DATABASE_INITIALIZATION_SETUP.md** - Database setup and initialization procedures
6. **STRUCTURED_LOGGING_GUIDE.md** - Structured logging implementation and usage
7. **CACHE_HIT_MISS_DETECTION_GUIDE.md** - Cache feature functionality and usage

**Use these files for:**
- Understanding the project
- Production deployment
- Feature documentation
- Configuration reference
- Initial setup and operation

### Development Notes (docs/dev-notes/)
See `docs/dev-notes/README.md` for detailed information.

**Subdirectories:**
- **debugging/** - Troubleshooting guides for issues encountered
- **analysis/** - Analysis documents from development phases
- **cache-docs/** - Reference material for cache implementation
- **logging-docs/** - Reference material for logging implementation
- **process-docs/** - Development process and policy documentation

**Use these files for:**
- Understanding development history
- Troubleshooting specific issues
- Detailed reference material
- Process guidelines

## Quick Navigation

### Getting Started
1. Start with `README.md` in project root
2. For deployment: `DEPLOYMENT_VALIDATION_REPORT.md`
3. For troubleshooting: `docs/dev-notes/debugging/`

### Feature Documentation
- **Cache:** `CACHE_HIT_MISS_DETECTION_GUIDE.md`
- **Logging:** `STRUCTURED_LOGGING_GUIDE.md`
- **Database:** `DATABASE_INITIALIZATION_SETUP.md`

### Fixing Issues
- Check `docs/dev-notes/debugging/` directory
- Review relevant issue fix guide
- See `PRE_DOCKER_AUDIT_REPORT.md` for known issues

### Development Process
- See `docs/dev-notes/process-docs/`
- Review commit message policy
- Understand workflow guidelines

## Contributing Documentation

### When Writing Essential Documentation
- Place in project root directory
- Include in README if not already there
- Ensure comprehensive coverage
- Keep updated with code changes

### When Writing Development Notes
- Place in appropriate `docs/dev-notes/` subdirectory
- Follow existing naming conventions
- Add entry to subdirectory README
- These files are NOT committed to version control by default

## Version Control

### Files Tracked (in git)
- Essential project documentation in root
- Main project README
- Feature documentation

### Files Excluded (in .gitignore)
- `docs/dev-notes/` directory - temporary development notes
- Individual analysis and debugging documents
- Reference materials created during development

This separation keeps the repository clean while preserving development context.

---

**Documentation Structure Established:** 2026-09-13  
**Total Essential Docs:** 7 files  
**Total Dev Notes:** 20 files in excluded directory  
**Total Documentation:** ~400 KB
