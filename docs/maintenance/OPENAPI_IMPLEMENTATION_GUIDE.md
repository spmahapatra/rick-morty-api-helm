# OpenAPI Decoupling: Practical Implementation Guide

**Document Version:** 1.0.0  
**Date:** 2026-09-13  
**Focus:** Step-by-step implementation for rick-morty-api project

---

## Quick Reference: Decision Tree

```
Your Project (rick-morty-api)
├─ Single monolithic app? YES
├─ <5 developers? YES
├─ Internal API only? YES
├─ Rapid iteration phase? YES
│
└─ RECOMMENDATION: Co-Locate NOW, Decouple LATER ✅
   Implement hybrid approach with validation
```

---

## Phase 1: Optimized Co-Location (Immediate)

### Step 1: Organize OpenAPI Structure

```bash
# Create spec directory
mkdir -p src/api/spec
mkdir -p src/api/spec/{paths,components,examples}

# Create main openapi.yaml
touch src/api/spec/openapi.yaml
```

**File Structure:**
```
src/api/spec/
├── openapi.yaml              (Main spec - refs other files)
├── info.yaml                 (API title, version, contact)
├── paths/
│   ├── characters.yaml       (GET /characters, POST /characters)
│   ├── episodes.yaml         (GET /episodes)
│   └── locations.yaml        (GET /locations)
├── components/
│   ├── schemas/
│   │   ├── Character.yaml
│   │   ├── Episode.yaml
│   │   └── Error.yaml
│   ├── responses/
│   │   ├── NotFound.yaml
│   │   └── Unauthorized.yaml
│   └── securitySchemes/
│       └── BearerAuth.yaml
└── examples/
    ├── character-list.yaml
    └── character-detail.yaml
```

### Step 2: Create Main OpenAPI Document

**File: `src/api/spec/openapi.yaml`**

```yaml
openapi: 3.1.0

info:
  $ref: './info.yaml'

servers:
  - url: http://localhost:8000
    description: Development
  - url: https://api.rickmortyexample.com
    description: Production

paths:
  /characters:
    $ref: './paths/characters.yaml#/paths/list'
  /characters/{id}:
    $ref: './paths/characters.yaml#/paths/detail'
  /episodes:
    $ref: './paths/episodes.yaml#/paths/list'
  /episodes/{id}:
    $ref: './paths/episodes.yaml#/paths/detail'
  /locations:
    $ref: './paths/locations.yaml#/paths/list'
  /locations/{id}:
    $ref: './paths/locations.yaml#/paths/detail'

components:
  schemas:
    Character:
      $ref: './components/schemas/Character.yaml'
    Episode:
      $ref: './components/schemas/Episode.yaml'
    Location:
      $ref: './components/schemas/Location.yaml'
    Error:
      $ref: './components/schemas/Error.yaml'
  
  responses:
    NotFound:
      $ref: './components/responses/NotFound.yaml'
    Unauthorized:
      $ref: './components/responses/Unauthorized.yaml'
  
  securitySchemes:
    BearerAuth:
      $ref: './components/securitySchemes/BearerAuth.yaml'

security:
  - BearerAuth: []

tags:
  - name: Characters
    description: Character related endpoints
  - name: Episodes
    description: Episode related endpoints
  - name: Locations
    description: Location related endpoints
```

**File: `src/api/spec/info.yaml`**

```yaml
title: Rick and Morty API
version: 1.0.0
description: |
  The Rick and Morty API provides access to character, episode,
  and location data from the Rick and Morty universe.
  
  ## Getting Started
  - Request an API key from the developer portal
  - Use Bearer token authentication
  - Rate limit: 1000 requests/hour
  
  ## API Versioning
  - Current version: 1.0.0
  - Deprecation policy: 18-month support
  - Breaking changes: Major version updates only

contact:
  name: API Support
  url: https://example.com/support
  email: api-support@example.com

license:
  name: MIT
  url: https://opensource.org/licenses/MIT
```

**File: `src/api/spec/paths/characters.yaml`**

```yaml
paths:
  list:
    get:
      tags:
        - Characters
      summary: List all characters
      operationId: listCharacters
      parameters:
        - name: page
          in: query
          description: Page number for pagination
          schema:
            type: integer
            default: 1
            minimum: 1
        - name: limit
          in: query
          description: Results per page
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100
      responses:
        '200':
          description: List of characters
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '../components/schemas/Character.yaml'
                  pagination:
                    type: object
                    properties:
                      page:
                        type: integer
                      limit:
                        type: integer
                      total:
                        type: integer
        '400':
          $ref: '../components/responses/BadRequest.yaml'
        '401':
          $ref: '../components/responses/Unauthorized.yaml'
    
    post:
      tags:
        - Characters
      summary: Create a new character
      operationId: createCharacter
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - species
              properties:
                name:
                  type: string
                species:
                  type: string
                status:
                  type: string
                  enum: [Alive, Dead, unknown]
      responses:
        '201':
          description: Character created
          content:
            application/json:
              schema:
                $ref: '../components/schemas/Character.yaml'
        '400':
          $ref: '../components/responses/BadRequest.yaml'
        '401':
          $ref: '../components/responses/Unauthorized.yaml'

  detail:
    get:
      tags:
        - Characters
      summary: Get character details
      operationId: getCharacter
      parameters:
        - name: id
          in: path
          required: true
          description: Character ID
          schema:
            type: string
      responses:
        '200':
          description: Character details
          content:
            application/json:
              schema:
                $ref: '../components/schemas/Character.yaml'
        '404':
          $ref: '../components/responses/NotFound.yaml'
```

**File: `src/api/spec/components/schemas/Character.yaml`**

```yaml
type: object
required:
  - id
  - name
  - species
properties:
  id:
    type: string
    format: uuid
    description: Unique character identifier
  name:
    type: string
    description: Character name
    minLength: 1
    maxLength: 255
  species:
    type: string
    description: Character species
    enum:
      - Human
      - Alien
      - Animal
      - Robot
      - Demon
      - unknown
  status:
    type: string
    description: Character status
    enum:
      - Alive
      - Dead
      - unknown
  gender:
    type: string
    enum:
      - Male
      - Female
      - Genderless
      - unknown
  image:
    type: string
    format: uri
    description: Character image URL
  created_at:
    type: string
    format: date-time
    description: Creation timestamp
  updated_at:
    type: string
    format: date-time
    description: Last update timestamp

example:
  id: "550e8400-e29b-41d4-a716-446655440000"
  name: "Rick Sanchez"
  species: "Human"
  status: "Alive"
  gender: "Male"
  image: "https://example.com/rick.png"
  created_at: "2024-01-01T00:00:00Z"
  updated_at: "2024-01-01T00:00:00Z"
```

### Step 3: Configure Package.json Scripts

```json
{
  "name": "rick-morty-api",
  "version": "1.0.0",
  "devDependencies": {
    "@stoplight/spectral-cli": "^6.11.0",
    "@openapitools/openapi-generator-cli": "^2.7.0",
    "@apidevtools/swagger-parser": "^10.1.0",
    "@types/jest": "^29.5.0",
    "jest": "^29.5.0",
    "openapi-types": "^12.1.0"
  },
  "scripts": {
    "validate:spec": "spectral lint src/api/spec/openapi.yaml --format pretty",
    "validate:spec-syntax": "swagger-cli validate src/api/spec/openapi.yaml",
    "validate:spec-code-sync": "ts-node scripts/validate-spec-code.ts",
    "validate:breaking-changes": "ts-node scripts/detect-breaking-changes.ts",
    "generate:types": "openapi-generator-cli generate -c config.yaml",
    "generate:client": "openapi-generator-cli generate -c client-config.yaml",
    "docs:api": "npx redoc-cli build src/api/spec/openapi.yaml -o public/api-docs.html",
    "test:contracts": "jest --testPathPattern=contracts",
    "test:all": "npm run validate:spec && npm run test:contracts && npm test"
  }
}
```

### Step 4: Set Up CI/CD Validation

**File: `.github/workflows/api-validation.yml`**

```yaml
name: API Validation

on:
  push:
    branches: [master, develop]
    paths:
      - 'src/api/spec/**'
      - 'src/handlers/**'
      - '.github/workflows/api-validation.yml'
  pull_request:
    branches: [master, develop]
    paths:
      - 'src/api/spec/**'
      - 'src/handlers/**'

jobs:
  validate-spec:
    name: Validate OpenAPI Spec
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      
      - name: Lint OpenAPI Spec
        run: npm run validate:spec
      
      - name: Validate Spec Syntax
        run: npm run validate:spec-syntax
      
      - name: Check Code-Spec Sync
        run: npm run validate:spec-code-sync
      
      - name: Detect Breaking Changes
        run: npm run validate:breaking-changes

  contract-tests:
    name: Contract Tests
    runs-on: ubuntu-latest
    needs: validate-spec
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      
      - run: npm run test:contracts

  generate-docs:
    name: Generate API Documentation
    runs-on: ubuntu-latest
    needs: validate-spec
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      
      - run: npm run docs:api
      
      - name: Upload API Docs
        uses: actions/upload-artifact@v3
        with:
          name: api-docs
          path: public/api-docs.html
```

---

## Phase 2: Transition to Decoupled (6+ months)

### When to Trigger Decoupling

```
Trigger Conditions:
✓ 2+ microservices in development
✓ Specs need to be shared
✓ Team expanded beyond 5 developers
✓ External API consumers requesting access
✓ Spec versioning needed independently
```

### Step 1: Create Specs Repository

```bash
# Create new repository
git init rick-morty-api-specs
cd rick-morty-api-specs

# Copy existing spec structure
cp -r ../rick-morty-api/src/api/spec/* ./

# Create package.json for publishing
cat > package.json << 'EOF'
{
  "name": "@rickmorty/openapi-specs",
  "version": "1.0.0",
  "description": "OpenAPI specifications for Rick and Morty API",
  "files": ["openapi", "CHANGELOG.md", "README.md"],
  "scripts": {
    "validate": "spectral lint openapi/3.1/openapi.yaml",
    "publish:npm": "npm publish"
  },
  "publishConfig": {
    "access": "public"
  }
}
EOF
```

### Step 2: Update Main Application Repository

**File: `package.json` (rick-morty-api)**

```json
{
  "dependencies": {
    "@rickmorty/openapi-specs": "^1.0.0"
  },
  "scripts": {
    "setup:specs": "npm install @rickmorty/openapi-specs",
    "generate:types": "openapi-generator-cli generate -i node_modules/@rickmorty/openapi-specs/openapi/3.1/openapi.yaml -c config.yaml"
  }
}
```

**File: `.gitignore` (remove specs)**

```
# Remove from co-location
src/api/spec/
```

**File: `src/generate-types.ts`** (new)

```typescript
import { spawn } from 'child_process';
import * as path from 'path';

const specPath = path.join(
  __dirname,
  '../node_modules/@rickmorty/openapi-specs/openapi/3.1/openapi.yaml'
);

spawn('openapi-generator-cli', [
  'generate',
  '-i', specPath,
  '-g', 'typescript',
  '-o', 'src/generated'
]);
```

### Step 3: Set Up Publishing Workflow

**File: `rick-morty-api-specs/.github/workflows/publish.yml`**

```yaml
name: Publish Specs to NPM

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          registry-url: 'https://registry.npmjs.org'
      
      - name: Validate Spec
        run: |
          npm install -g @stoplight/spectral-cli
          spectral lint openapi/3.1/openapi.yaml
      
      - name: Publish
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

---

## Workflow Commands Reference

### Local Development Workflow

```bash
# Start development
git checkout -b feature/add-search develop

# Edit spec
vim src/api/spec/paths/characters.yaml

# Validate changes
npm run validate:spec
npm run validate:spec-code-sync

# Implement endpoint
vim src/handlers/search.ts

# Test contract
npm run test:contracts

# Commit
git add src/
git commit -m "feat: add character search endpoint"

# Push and create PR
git push origin feature/add-search
```

### Decoupled Workflow (Future)

```bash
# Spec repository changes
cd rick-morty-api-specs
git checkout -b feature/add-search develop
vim openapi/3.1/paths/characters.yaml
npm run validate
git commit -m "feat(spec): add character search endpoint"
git push origin feature/add-search
# → Create PR, review, merge to develop

# Prepare release
git checkout master
git merge develop
git tag v1.1.0
git push origin master --tags
# → CI/CD publishes to npm

# Application repository updates
cd rick-morty-api
npm install @rickmorty/openapi-specs@1.1.0
npm run generate:types
git add package.json package-lock.json src/generated/
git commit -m "chore: update specs to v1.1.0"
git checkout -b feature/implement-search develop
vim src/handlers/search.ts
npm run test:contracts
git push origin feature/implement-search
# → Create PR, review, merge
```

---

## Complete Example: Adding New Endpoint

### Spec-First Development (Recommended)

**Step 1: Design Endpoint in Spec**

```bash
git checkout -b feature/character-filter develop
```

Edit `src/api/spec/paths/characters.yaml`:

```yaml
get:
  summary: List characters with advanced filtering
  operationId: listCharactersFiltered
  parameters:
    - name: species
      in: query
      schema:
        type: string
        enum: [Human, Alien, Robot, unknown]
    - name: status
      in: query
      schema:
        type: string
        enum: [Alive, Dead, unknown]
    - name: name
      in: query
      schema:
        type: string
```

**Step 2: Validate Spec**

```bash
npm run validate:spec
# Output: ✅ Spec is valid
```

**Step 3: Generate Types**

```bash
npm run generate:types
# Generates src/generated/types.ts with:
# - CharacterFilter interface
# - ListCharactersRequest
# - ListCharactersResponse
```

**Step 4: Implement Handler**

```typescript
// src/handlers/listCharacters.ts
import { Request, Response } from 'express';
import { ListCharactersRequest } from '../generated/types';

export async function listCharacters(
  req: ListCharactersRequest,
  res: Response
) {
  const { species, status, name } = req.query;
  
  // Implementation guided by spec types
  const characters = await Character.find({
    ...(species && { species }),
    ...(status && { status }),
    ...(name && { name: new RegExp(name, 'i') })
  });
  
  res.json({
    data: characters,
    pagination: { page: 1, limit: 20, total: characters.length }
  });
}
```

**Step 5: Add Contract Tests**

```typescript
// tests/contracts/characters.test.ts
describe('Character Filter Contract', () => {
  test('GET /characters?species=Human matches spec', async () => {
    const response = await request(app)
      .get('/characters')
      .query({ species: 'Human' });
    
    expect(response.status).toBe(200);
    // Response automatically validated against spec schema
  });
});
```

**Step 6: Commit**

```bash
git add src/
git commit -m "feat(api): implement character filtering

- Add species, status, name query parameters
- Implement filtering logic with regex matching
- Add contract tests validating against spec
- All changes conform to OpenAPI 3.1 spec"
```

---

## Troubleshooting

### Common Issues

**Issue: Spec validation fails**
```bash
npm run validate:spec
# Error: "properties: Missing object key 'type'"

# Fix: Add 'type: object' to schema
```

**Issue: Code-spec sync validation fails**
```bash
npm run validate:spec-code-sync
# Error: "Endpoint GET /characters in spec but not implemented"

# Fix: Implement the handler in src/handlers/
```

**Issue: Contract tests fail**
```bash
npm run test:contracts
# Error: "Response schema does not match spec"

# Fix: Update response to match spec schema
```

---

## Summary: Next Steps

### Immediate (This Week)
- [ ] Create `src/api/spec/` directory
- [ ] Move/create OpenAPI files
- [ ] Add npm scripts for validation
- [ ] Update CI/CD with validation

### Short Term (This Month)
- [ ] Add contract tests
- [ ] Generate types from spec
- [ ] Document spec contribution process
- [ ] Train team on workflow

### Medium Term (3 months)
- [ ] Stabilize spec
- [ ] Gather feedback
- [ ] Plan decoupling if needed
- [ ] Document lessons learned

### Long Term (6+ months)
- [ ] Create specs repository if 2+ services
- [ ] Publish to NPM
- [ ] Migrate services to use decoupled specs
- [ ] Establish spec governance

---

**Version:** 1.0.0  
**Status:** Ready for Implementation
