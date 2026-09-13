# Commit Message Policy

## Overview

This project strictly enforces **Conventional Commits** format for all commit messages. This standard provides:
- Clear communication of changes
- Semantic versioning compatibility
- Automated changelog generation capability
- Searchable commit history

---

## Format Specification

### Required Format

```
type(scope): subject

optional body

optional footer
```

### Anatomy

```
feat(api): add character filtering by origin
 │    │     │
 │    │     └─ subject: lowercase, imperative, no period
 │    └─────── scope: optional, lowercase, in parentheses
 └──────────── type: one of the allowed types
```

---

## Commit Types

| Type | Purpose | Example |
|------|---------|---------|
| **feat** | New feature | `feat(api): add pagination support` |
| **fix** | Bug fix | `fix(filtering): resolve Earth origin matching` |
| **docs** | Documentation only | `docs: update README installation steps` |
| **style** | Code style (formatting, semicolons) | `style(app): format imports alphabetically` |
| **refactor** | Code refactoring (no behavior change) | `refactor(client): simplify fetch method` |
| **perf** | Performance improvement | `perf(pagination): optimize character queries` |
| **test** | Add/update tests | `test(api): add edge case test scenarios` |
| **chore** | Build, dependencies, tooling | `chore: update Flask to 3.0.1` |
| **ci** | CI/CD configuration | `ci: add GitHub Actions workflow` |
| **build** | Build system changes | `build: add Dockerfile multi-stage optimization` |

---

## Scope Guidelines

Scope should be optional but recommended. Use:
- **Lowercase** only
- **Hyphen-separated** for multi-word scopes
- Short identifiers (1-3 words max)

### Example Scopes

```
feat(api): add new endpoint
feat(filtering): improve origin matching
feat(pagination): implement offset-based paging
feat(error-handling): add timeout protection
feat(docs): create API reference
feat(docker): optimize container image
```

---

## Subject Line Rules

1. **Start with lowercase** (except for acronyms like `API`)
   - ✅ `feat(api): add endpoint`
   - ❌ `feat(api): Add endpoint`

2. **Use imperative mood** (as if commanding an action)
   - ✅ `feat(api): add pagination` (what the code does)
   - ❌ `feat(api): adds pagination` (describes what was done)
   - ❌ `feat(api): added pagination` (past tense)

3. **No period at end**
   - ✅ `feat(api): add pagination support`
   - ❌ `feat(api): add pagination support.`

4. **Keep it concise** (50 characters or less)
   - ✅ `feat(api): add pagination`
   - ❌ `feat(api): implement offset-based pagination with configurable limits`

5. **Be specific about the change**
   - ✅ `fix(filtering): resolve Earth origin matching for variants`
   - ❌ `fix: fix bug`

---

## Body (Optional)

Use the body for longer commit messages:

```
feat(pagination): implement offset-based paging

- Add page parameter for result offset
- Add limit parameter (1-50, default 10)
- Return pagination metadata (current_page, total_pages)
- Include navigation flags (has_next, has_previous)
```

### Body Rules

1. Separate from subject by blank line
2. Explain **what** and **why**, not **how**
3. Wrap at 72 characters
4. Use bullet points for multiple changes
5. Reference issues using keywords: `Fixes #123`, `Closes #456`

---

## Footer (Optional)

Use footer for issue references:

```
feat(api): add character filtering

Implement filtering for human, alive characters from Earth variants.

Fixes #42
Closes #156
```

### Recognized Keywords

- `Fixes #issue` - Closes issue automatically
- `Closes #issue` - Closes issue automatically
- `Resolves #issue` - Closes issue automatically
- `Related to #issue` - Links without closing
- `BREAKING CHANGE:` - Indicates breaking change

---

## Examples

### ✅ CORRECT Format

```
feat(api): add character filtering
```

```
fix(pagination): resolve off-by-one error
```

```
docs: update installation instructions
```

```
test(sorting): add descending order test cases
```

```
refactor(client): simplify request handling
```

```
chore: update dependencies
```

```
feat(api): implement pagination

- Add page and limit query parameters
- Return metadata about pagination state
- Support configurable page sizes (1-50)
- Default page size is 10 items

Fixes #42
```

### ❌ INCORRECT Format

```
Updated API
```
→ Missing type and subject

```
FEAT: Add Pagination
```
→ Type should be lowercase, subject should be lowercase

```
feat: add pagination.
```
→ Subject ends with period

```
feat: Added pagination
```
→ Should use imperative mood (add, not added)

```
feat(API-ENDPOINTS): add new feature
```
→ Scope should be lowercase and hyphen-separated

```
fix bug in filtering
```
→ Missing type prefix

---

## Enforcement

This repository uses **git hooks** to automatically validate commit messages:

- **Hook Location**: `.git/hooks/prepare-commit-msg`
- **When it runs**: Before each commit
- **What it checks**: Format compliance

### Running a Commit

```bash
git commit -m "feat(api): add pagination support"
```

If your message is invalid, the commit is rejected with helpful error guidance.

### Bypassing (NOT RECOMMENDED)

```bash
git commit -m "invalid message" --no-verify
```

⚠️ **Do not use** `--no-verify` to bypass validation. It defeats the purpose of standardization.

---

## Practical Workflow

### Scenario 1: Simple Bug Fix

```bash
git commit -m "fix(filtering): resolve Earth origin variant matching"
```

### Scenario 2: New Feature with Details

```bash
git commit -m "feat(pagination): implement offset-based paging

- Add page and limit query parameters
- Support configurable limits (1-50, default 10)
- Return pagination metadata in response
- Include has_next and has_previous flags

Fixes #42"
```

### Scenario 3: Documentation Update

```bash
git commit -m "docs: add API endpoint examples to README"
```

### Scenario 4: Refactoring

```bash
git commit -m "refactor(client): simplify character fetch method"
```

### Scenario 5: Test Addition

```bash
git commit -m "test(sorting): add ascending and descending order test cases"
```

---

## Integration with Tooling

### Changelog Generation

This format enables automated changelog generation:

```bash
conventional-changelog -p angular -r 2 > CHANGELOG.md
```

Generates changelog sections:
- **Features** (feat)
- **Bug Fixes** (fix)
- **Breaking Changes** (BREAKING CHANGE footer)

### Semantic Versioning

Commits automatically determine version bumps:
- `feat:` → Minor version bump (0.1.0 → 0.2.0)
- `fix:` → Patch version bump (0.1.0 → 0.1.1)
- `BREAKING CHANGE:` → Major version bump (0.1.0 → 1.0.0)

### Git History Search

Easy to search commits by type:

```bash
# Find all features
git log --oneline --grep="^feat"

# Find all bug fixes
git log --oneline --grep="^fix"

# Find commits affecting API
git log --oneline --grep="\(api\)"
```

---

## Initial Commit Reference

The initial commit for this project follows this format:

```
commit 22a44d6

feat: implement Rick and Morty Character API with filtering and pagination

- Implement RickAndMortyClient for upstream API communication
- Add character filtering by origin (Earth variants), species (Human), and status (Alive)
- Implement offset-based pagination with configurable limits (1-50, default 10)
- Add sorting by name and ID with ascending/descending order
- Create four REST endpoints:
  - GET / - API documentation and endpoint reference
  - GET /health - Health check endpoint
  - GET /characters - List filtered characters with pagination and sorting
  - GET /characters/<id> - Retrieve individual character by ID
- Implement comprehensive error handling with status code mapping
- Add input validation for query parameters
- Create custom RickAndMortyAPIError exception class
- Implement 10-second timeout protection
- Add 16 unit tests covering all functionality
- Create Flask and CORS configuration
- Create Dockerfile for containerization
- Add docker-compose configuration for deployment
- Include gunicorn for production serving
- Add comprehensive README with examples
- Add environment configuration template (.env.example)
- Implement all code documentation with docstrings
```

---

## Team Guidelines

1. **Always write meaningful messages** - Future developers (including yourself) will thank you
2. **Use lowercase** - Consistency matters
3. **Be specific** - "fix pagination bug" is better than "fix bug"
4. **Use scope** - Helps organize commits by component
5. **Follow the format** - The git hook enforces it
6. **Don't bypass validation** - Resist the urge to use `--no-verify`

---

## Questions & Answers

**Q: Can I use ALL CAPS for types?**  
A: No. Types must be lowercase: `feat`, `fix`, not `FEAT`, `FIX`.

**Q: Can the scope have uppercase?**  
A: No. Scope must be lowercase: `api`, `user-service`, not `API`, `UserService`.

**Q: Do I need a scope?**  
A: No, it's optional. But recommended for clarity.

**Q: Can I include AI mentions in commit messages?**  
A: Yes, but keep focus on the technical change. Example:  
`feat(api): add pagination support` (preferred)  
`feat(api): implement pagination` (also acceptable)

**Q: What if my message doesn't fit the rules?**  
A: The git hook will reject it and show you the correct format. Re-run with valid format.

**Q: Can I use emoji in commit messages?**  
A: Not in type section. Examples:  
❌ `🎉 feat(api): add pagination`  
✅ `feat(api): add pagination support 🎉`

---

## Permanent Rules

These rules apply to **ALL** commits in this repository:

- ✅ Must use Conventional Commits format
- ✅ Type is mandatory and must be from approved list
- ✅ Subject must be lowercase (except acronyms)
- ✅ Subject must not end with period
- ✅ Must use imperative mood
- ✅ Scope recommended but optional
- ✅ Body should explain what/why not how
- ✅ Git hooks will enforce these rules automatically
- ✅ No bypass without explicit review

---

## Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Angular Contributing Guide](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)
- [Semantic Versioning](https://semver.org/)

---

**Established**: 2026-09-13  
**Enforcement**: Automatic via Git hooks  
**Scope**: All commits in this repository  
