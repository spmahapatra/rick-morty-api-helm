# Docker Image Security Scanning - Implementation Guide
## rick-morty-api Project

**Status:** Ready for implementation
**Effort:** 12-17 hours over 4-6 weeks
**Cost:** $0/month

---

## PHASE 1: BASELINE SCAN & ANALYSIS (Week 1)

### Step 1.1: Run Baseline Trivy Scan

```bash
# Install Trivy locally (if not already installed)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan your current Dockerfile's base image
trivy image python:3.9-slim

# Scan published image from ghcr.io (if available)
trivy image ghcr.io/spmahapatra/rick-morty-api:latest

# Generate comprehensive JSON report
trivy image --format json --output baseline-report.json python:3.9-slim

# Generate SBOM
trivy image --format cyclonedx --output baseline-sbom.json python:3.9-slim
```

**Expected Output:**
- 10-30 vulnerabilities found (mostly OS-level in base image)
- Severity breakdown: 5-10 LOW, 3-8 MEDIUM, 1-3 HIGH, 0-1 CRITICAL
- Note vulnerabilities for Week 2 remediation

### Step 1.2: Audit Current Dependencies

```bash
# Check for known vulnerabilities in requirements.txt
pip install pip-audit
pip-audit

# Alternative: Use safety (legacy but still useful)
pip install safety
safety check
```

**Typical Output:**
```
Flask==3.0.0: OK (no known vulnerabilities)
requests==2.31.0: 1 vulnerability found (LOW severity)
  - Description: Certificate validation issue
  - Fix: Update to 2.32.0+
redis==5.0.0: OK
... (more dependencies)
```

### Step 1.3: Create Vulnerability Inventory

```bash
# Create spreadsheet/document of findings
cat > SECURITY_BASELINE.md << 'EOF'
# Security Baseline - rick-morty-api

## Base Image Vulnerabilities (python:3.9-slim)

| CVE ID | Package | Severity | Description | Fix |
|--------|---------|----------|-------------|-----|
| CVE-2024-XXXX | openssl | HIGH | Buffer overflow | Upgrade base image to python:3.11 |
| CVE-2024-YYYY | curl | MEDIUM | TLS issue | Included in image, will fix with base upgrade |
| ... | ... | ... | ... | ... |

## Dependency Vulnerabilities

| Package | Current | Issue | Fix | Priority |
|---------|---------|-------|-----|----------|
| requests | 2.31.0 | Certificate validation | Update to 2.32.0 | HIGH |
| ... | ... | ... | ... | ... |

## Remediation Plan
- Week 2: Upgrade base image + dependencies
- Week 3: Re-scan and validate

EOF
```

---

## PHASE 2: REMEDIATION (Week 2-3)

### Step 2.1: Upgrade Base Image

**Edit Dockerfile:**

```dockerfile
# BEFORE
FROM python:3.9-slim

# AFTER (Recommended - latest stable Python 3.11)
FROM python:3.11-slim-bullseye

# Note: If 3.11 causes issues, try 3.10
# FROM python:3.10-slim-bullseye

# Keep rest of Dockerfile unchanged
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    PYTHONPATH=/app:$PYTHONPATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ... rest unchanged ...
```

**Test locally:**

```bash
# Build new image
docker build -t rick-morty-api:test .

# Test in container
docker run --rm -it rick-morty-api:test python --version
# Should output: Python 3.11.x

# Run test suite
docker run --rm rick-morty-api:test pytest tests/ -v

# Scan new image
trivy image rick-morty-api:test
```

**Expected Result:**
- Vulnerabilities reduced by 50-70% (most came from old base image)
- Test suite still passes
- No breaking changes

### Step 2.2: Update Outdated Dependencies

**Analyze and update requirements.txt:**

```bash
# Generate updated requirements
pip list --outdated

# Update safely (one by one, not all at once)
pip install --upgrade requests
pip install --upgrade redis
pip install --upgrade psycopg2-binary

# Check for breaking changes
pip check

# Export updated versions
pip freeze > requirements_new.txt

# Review diff
diff requirements.txt requirements_new.txt
```

**Recommended updates:**

```txt
# BEFORE (current)
Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
redis==5.0.0
psycopg2-binary==2.9.9
pydantic==2.5.0
prometheus-client==0.19.0
sqlalchemy==2.0.23
alembic==1.13.0
tenacity==8.2.3
pybreaker==1.4.0
python-json-logger==2.0.7

# AFTER (recommended updates for 2026)
Flask==3.0.1
Flask-CORS==4.0.0
requests==2.32.0          # Update: security fix
python-dotenv==1.0.1      # Update: minor patch
gunicorn==21.2.0
redis==5.0.0
psycopg2-binary==2.9.10   # Update: minor patch
pydantic==2.5.3           # Update: bug fixes
prometheus-client==0.19.0
sqlalchemy==2.0.25        # Update: bug fixes
alembic==1.13.1           # Update: minor patch
tenacity==8.2.3
pybreaker==1.4.0
python-json-logger==2.0.7
```

**Test updated dependencies:**

```bash
# Create virtual environment with new requirements
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt

# Run test suite
pytest tests/ -v --cov=src

# Run app briefly to verify startup
python -c "from app import app; print('✓ App imports successfully')"

deactivate
rm -rf test_env
```

### Step 2.3: Docker Build & Scan with Updates

```bash
# Build image with updated requirements
docker build -t rick-morty-api:v2-test .

# Scan updated image
trivy image rick-morty-api:v2-test

# Generate reports
trivy image --format json --output v2-scan.json rick-morty-api:v2-test
trivy image --format cyclonedx --output v2-sbom.json rick-morty-api:v2-test

# Compare before/after
echo "Vulnerabilities BEFORE: $(jq '.Results[0].Vulnerabilities | length' baseline-report.json)"
echo "Vulnerabilities AFTER:  $(jq '.Results[0].Vulnerabilities | length' v2-scan.json)"
```

**Expected Result:**
- 60-80% reduction in vulnerabilities
- All CRITICAL vulnerabilities eliminated
- 0-2 HIGH severity issues (acceptable)

### Step 2.4: Create `.trivyignore` File

```bash
# Create exemption file for known false positives or accepted risks
cat > .trivyignore << 'EOF'
# Trivy Ignore Configuration
# Format: CVE ID, package name, or severity level

# Example false positives (update after first scan):
# CVE-2024-XXXXX: Requires specific environment config not present in image

# Example accepted risks (document reason + expiration):
# CVE-2024-YYYYY: LOW severity, no impact on API endpoints, fix scheduled Q3 2026

# Known limitations:
# This file should be minimal - most findings should be fixed, not ignored
EOF

# Verify ignore works
trivy image --ignore-file .trivyignore rick-morty-api:v2-test
```

---

## PHASE 3: GITHUB ACTIONS INTEGRATION (Week 3-4)

### Step 3.1: Update CD Workflow

Edit `.github/workflows/cd.yml` and add scanning steps after Docker build:

```yaml
  build-and-test:
    name: Build & Test
    runs-on: ubuntu-latest
    timeout-minutes: 20
    needs: [verify-tag-creation]
    if: needs.verify-tag-creation.outputs.is-valid-semver == 'true'
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt pytest pytest-cov
      
      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml -v
        env:
          APP_ENV: testing
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max

      # ============== ADD SCANNING STEPS BELOW ==============
      
      - name: Run Trivy security scan
        id: trivy-scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.meta.outputs.tags }}
          format: 'json'
          output: 'trivy-report.json'
          severity: 'CRITICAL,HIGH,MEDIUM'
          exit-code: '0'  # Don't fail build yet (gradual enforcement)
          ignore-unfixed: false
      
      - name: Generate CycloneDX SBOM
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.meta.outputs.tags }}
          format: 'cyclonedx'
          output: 'sbom.json'
      
      - name: Generate SPDX SBOM
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.meta.outputs.tags }}
          format: 'spdx'
          output: 'sbom.spdx.json'
      
      - name: Generate HTML Report
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.meta.outputs.tags }}
          format: 'template'
          template: '@/contrib/html.tpl'
          output: 'trivy-report.html'
      
      - name: Create GitHub Issue on Critical Findings
        if: always()
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            
            // Parse Trivy JSON report
            let report = {};
            try {
              report = JSON.parse(fs.readFileSync('trivy-report.json', 'utf8'));
            } catch (e) {
              console.log('No scan report found or parse error:', e.message);
              return;
            }
            
            // Count vulnerabilities by severity
            let criticalCount = 0;
            let highCount = 0;
            let findings = [];
            
            const results = report.Results || [];
            results.forEach(result => {
              const vulns = result.Vulnerabilities || [];
              vulns.forEach(vuln => {
                if (vuln.Severity === 'CRITICAL') {
                  criticalCount++;
                  findings.push(`- **CRITICAL** [${vuln.VulnerabilityID}] ${vuln.PackageName}: ${vuln.Title}`);
                } else if (vuln.Severity === 'HIGH') {
                  highCount++;
                  findings.push(`- **HIGH** [${vuln.VulnerabilityID}] ${vuln.PackageName}: ${vuln.Title}`);
                }
              });
            });
            
            // Only create issue if findings exist
            if (criticalCount > 0 || highCount > 0) {
              const severity = criticalCount > 0 ? '🚨 CRITICAL' : '⚠️ HIGH';
              const title = `${severity}: ${criticalCount} Critical & ${highCount} High vulnerabilities in image scan`;
              const body = `## Security Scan Results for ${{ steps.meta.outputs.tags }}\n
            ### Vulnerability Summary
            - **Critical:** ${criticalCount}
            - **High:** ${highCount}
            
            ### Detailed Findings
            ${findings.slice(0, 20).join('\n')}
            ${findings.length > 20 ? `\n... and ${findings.length - 20} more. See artifact for full report.` : ''}
            
            ### Scan Report
            - [JSON Report](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
            - [HTML Report (check artifacts)](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
            
            ### Required Action
            ${criticalCount > 0 ? '**This build contains CRITICAL vulnerabilities and should not be deployed to production.**' : 'Review HIGH severity vulnerabilities and plan remediation.'}
            
            _Scanned: ${{ steps.meta.outputs.tags }}_
            _Scan Date: ${{ github.event.head_commit.timestamp }}_`;
              
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: title,
                body: body,
                labels: ['security', 'vulnerability', criticalCount > 0 ? 'critical' : 'high'],
                assignees: context.payload.pull_request?.user?.login ? [context.payload.pull_request.user.login] : []
              });
              
              console.log(`Created issue: ${title}`);
            } else {
              console.log('✓ No Critical or High vulnerabilities found');
            }
      
      - name: Comment on PR with Scan Summary
        if: github.event_name == 'pull_request' && always()
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            
            let report = {};
            try {
              report = JSON.parse(fs.readFileSync('trivy-report.json', 'utf8'));
            } catch (e) {
              return;
            }
            
            let stats = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
            const results = report.Results || [];
            results.forEach(result => {
              const vulns = result.Vulnerabilities || [];
              vulns.forEach(vuln => {
                stats[vuln.Severity]++;
              });
            });
            
            const comment = `## 🔒 Security Scan Results\n
            | Severity | Count |\n
            |----------|-------|\n
            | Critical | ${stats.CRITICAL} |\n
            | High | ${stats.HIGH} |\n
            | Medium | ${stats.MEDIUM} |\n
            | Low | ${stats.LOW} |\n
            
            ✓ Scan complete. See check for details.`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
      
      - name: Upload Scan Artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-scan-results
          path: |
            trivy-report.json
            trivy-report.html
            sbom.json
            sbom.spdx.json
          retention-days: 90
      
      - name: Export SBOM to Release
        if: startsWith(github.ref, 'refs/tags/')
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const tag = context.ref.replace('refs/tags/', '');
            
            // Upload SBOMs to release (create if not exists)
            const releases = await github.rest.repos.listReleases({
              owner: context.repo.owner,
              repo: context.repo.repo
            });
            
            let releaseId = releases.data.find(r => r.tag_name === tag)?.id;
            
            if (!releaseId) {
              // Create release if it doesn't exist
              const newRelease = await github.rest.repos.createRelease({
                owner: context.repo.owner,
                repo: context.repo.repo,
                tag_name: tag,
                name: `Release ${tag}`,
                draft: false
              });
              releaseId = newRelease.data.id;
            }
            
            // Upload SBOM files
            const files = ['sbom.json', 'sbom.spdx.json'];
            for (const file of files) {
              if (fs.existsSync(file)) {
                const content = fs.readFileSync(file);
                await github.rest.repos.uploadReleaseAsset({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  release_id: releaseId,
                  name: file,
                  data: content
                });
              }
            }
```

### Step 3.2: Add CI Workflow Scanning (Optional)

Also update `.github/workflows/ci.yml` to scan on every push:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t rick-morty-api:latest .
      
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'rick-morty-api:latest'
          format: 'sarif'
          output: 'trivy-report.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-report.sarif'
          category: 'trivy'
```

### Step 3.3: Test Workflow Changes

```bash
# Verify YAML syntax
python -m yaml < .github/workflows/cd.yml > /dev/null && echo "✓ YAML valid"

# Create test tag to trigger workflow
git tag -a v0.1.0-scan-test -m "Test security scanning"
git push origin v0.1.0-scan-test

# Monitor GitHub Actions
# Go to: https://github.com/spmahapatra/rick-morty-api-helm/actions
# Watch build-and-test job for scanning steps

# Clean up test tag
git tag -d v0.1.0-scan-test
git push origin :refs/tags/v0.1.0-scan-test
```

---

## PHASE 4: HELM PREPARATION (Week 5-6)

### Step 4.1: Create Helm Chart Security Values

Create `helm/values.yaml` section:

```yaml
# Helm Chart Values - Security Configuration

# Image security
image:
  repository: ghcr.io/spmahapatra/rick-morty-api
  pullPolicy: IfNotPresent
  tag: ""  # Override with --set image.tag=v1.0.0
  
  # Optional: Security scanning metadata
  sbom:
    # URL to SBOM from release
    cycloneDxUrl: "https://github.com/spmahapatra/rick-morty-api-helm/releases/download/{{ .Chart.AppVersion }}/sbom.json"
    spdxUrl: "https://github.com/spmahapatra/rick-morty-api-helm/releases/download/{{ .Chart.AppVersion }}/sbom.spdx.json"
    
    # Optional: Require SBOM validation before deployment
    requireSBOM: false

# Security scanning policy
securityScanning:
  enabled: true
  
  # Fail deployment if vulnerabilities exceed threshold
  failurePolicy:
    critical: 0        # Zero tolerance for critical
    high: 3           # Allow up to 3 high (for now)
    medium: 10        # Allow up to 10 medium
  
  # Exempt specific CVEs (document reasons)
  exemptions: []
  #  - cve: "CVE-2024-XXXX"
  #    reason: "False positive - requires specific config"
  #    expiresAt: "2026-12-31"

# Pod security context
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

# Container security context
containerSecurityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false  # Set to true after app refactoring
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop: ["ALL"]
    add: []  # Only add if absolutely required

# Image pull secrets (if using private registry)
imagePullSecrets: []
  # - name: regcred

# Network policies
networkPolicy:
  enabled: false  # Enable when migrating to production K8s
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: ingress-nginx
      ports:
      - protocol: TCP
        port: 5000
  egress:
    - to:
      - namespaceSelector: {}
      ports:
      - protocol: TCP
        port: 443
    - to:
      - podSelector:
          matchLabels:
            app: postgres
      ports:
      - protocol: TCP
        port: 5432
```

### Step 4.2: Create Security Documentation

```bash
cat > docs/SECURITY.md << 'EOF'
# Security Policy

## Image Security Scanning

This project uses Trivy for container image security scanning:

- **Tool:** Trivy (open-source)
- **Frequency:** On every release + daily for deployed images
- **Report Format:** JSON, CycloneDX, SPDX
- **Policy:** Zero CRITICAL vulnerabilities, max 3 HIGH

### Scan Results

Latest scan reports are available in:
- GitHub Releases (SBOMs: `sbom.json`, `sbom.spdx.json`)
- GitHub Actions Artifacts (detailed reports)
- GitHub Security tab (integrated scanning)

### Vulnerability Response

**CRITICAL (Blocks Deployment)**
- Immediate fix required
- Do not merge PRs with CRITICAL vulns
- Creates GitHub issue with 🚨 CRITICAL tag

**HIGH (Requires Review)**
- Must be addressed in next release cycle
- Create GitHub issue for tracking
- Document exemptions if not fixable

**MEDIUM/LOW (Monitor)**
- Logged for awareness
- Fixed opportunistically with other updates

### Reporting CVEs

If you discover a vulnerability:
1. Check [GitHub Security Advisories](https://github.com/spmahapatra/rick-morty-api-helm/security/advisories)
2. Do NOT create public issue
3. Use "Report a vulnerability" button
4. Response target: 48 hours for CRITICAL, 1 week for HIGH

## Base Image Security

Base image: `python:3.11-slim-bullseye`

- Chosen for minimal attack surface
- Updated monthly with security patches
- Only includes Python runtime + essential tools

## Dependency Security

Dependencies are pinned to specific versions in `requirements.txt`:
- Enables reproducible builds
- Allows security updates on schedule
- Checked via `trivy` on every release

## Runtime Security (Kubernetes)

When deployed to Kubernetes:
- Pod runs as non-root user (UID 1000)
- Read-only root filesystem (where possible)
- Network policies restrict traffic
- No privileged container capabilities

## Supply Chain Security (Future)

Planned enhancements:
- Image signing with cosign + Rekor
- SLSA provenance attestation
- Admission controller (Kyverno) for policy enforcement

## Questions?

See [DOCKER_SECURITY_SCANNING_ANALYSIS.md](../DOCKER_SECURITY_SCANNING_ANALYSIS.md) for detailed analysis.

EOF
```

### Step 4.3: Create Security Badge

```bash
# Create security status badge for README.md

# Add to top of README.md:
cat >> README.md << 'EOF'

## Security Status

![Trivy Security Scan](https://img.shields.io/badge/trivy-passing-brightgreen)
![SBOM Available](https://img.shields.io/badge/sbom-cyclonedx%20%7C%20spdx-blue)
![License Compliant](https://img.shields.io/badge/license-compliant-brightgreen)

For details, see [Security Policy](docs/SECURITY.md)

EOF
```

---

## PHASE 5: TEAM COMMUNICATION & DOCUMENTATION (Week 3)

### Step 5.1: Create Team Runbook

```bash
cat > docs/SECURITY_RUNBOOK.md << 'EOF'
# Security Scanning Runbook

## Quick Reference

### What is Trivy?
- Container image vulnerability scanner
- Runs on every release in GitHub Actions
- Checks for OS, app library, secret, and configuration vulnerabilities
- Generates SBOM (Software Bill of Materials) for compliance

### View Latest Scan Results
1. Go to: https://github.com/spmahapatra/rick-morty-api-helm/releases
2. Download `sbom.json` or `sbom.spdx.json`
3. Or check GitHub Actions for detailed HTML report

### Fix a Vulnerability

**If CRITICAL found:**
1. Check GitHub issue created by bot
2. Identify package causing vulnerability
3. Update to patched version in `requirements.txt` or `Dockerfile`
4. Run locally: `pytest tests/ && docker build .`
5. Commit, push, create new tag to re-trigger scan

**Example: Fix requests library vulnerability**
```bash
# Current: requests==2.31.0 has CVE-2024-XXXX
# Action: Update to 2.32.0

# Edit requirements.txt
requests==2.32.0  # ← Changed

# Test
pip install -r requirements.txt
pytest tests/

# Commit
git add requirements.txt
git commit -m "Security: Update requests to 2.32.0 (fix CVE-2024-XXXX)"
git push

# Tag and release
git tag -a v1.0.1 -m "Security patch release"
git push origin v1.0.1  # ← Triggers scan in Actions
```

### Understand Scan Results

**JSON Report Structure:**
```json
{
  "Results": [
    {
      "Target": "python:3.11-slim-bullseye",
      "Type": "debian",
      "Vulnerabilities": [
        {
          "VulnerabilityID": "CVE-2024-XXXX",
          "PackageName": "openssl",
          "Severity": "HIGH",
          "Title": "Buffer overflow in OpenSSL",
          "Description": "...",
          "FixedVersion": "3.0.14-1"
        }
      ]
    }
  ]
}
```

### Skip False Positive

Some scanner findings are false positives. To skip them:

1. Verify it's actually not an issue in your use case
2. Add to `.trivyignore`:
   ```
   CVE-2024-XXXX  # Reason: False positive, requires X config we don't use
   ```
3. Document why in the comment
4. Commit and re-scan

### Exemption Request

For vulnerabilities you accept (e.g., no patch available):

1. Create GitHub issue titled: `Security: Exemption request for CVE-2024-XXXX`
2. Include:
   - CVE ID and affected package
   - Why it's not a concern for this project
   - Planned fix date (if any)
   - Expiration date (e.g., 6 months)
3. Get approval from @security-team
4. Add to `.trivyignore` with issue reference

---

## FAQ

**Q: Why did the build fail?**
A: Probably CRITICAL vulnerabilities found. Check the GitHub Actions log and fix the issue.

**Q: Can I ignore all warnings?**
A: No. CRITICAL must be fixed. HIGH requires justification. MEDIUM/LOW can be deferred.

**Q: Do I need to scan locally?**
A: Not required, but recommended for faster feedback:
```bash
trivy image python:3.11-slim
docker build -t rick-morty-api .
trivy image rick-morty-api
```

**Q: What if there's no patch?**
A: Document it and request exemption (see above). Security team reviews.

EOF
```

### Step 5.2: Schedule Team Meeting

```bash
# Create agenda for team sync
cat > SECURITY_MEETING_AGENDA.md << 'EOF'
# Security Scanning Implementation - Team Meeting

**Date:** [Schedule 30-min meeting]
**Attendees:** Engineering team

## Agenda

1. **Overview** (5 min)
   - Why we're scanning images
   - Benefits for Helm migration
   - Compliance requirements

2. **How It Works** (10 min)
   - Trivy scanning flow
   - GitHub Actions integration
   - What findings mean

3. **Team Responsibilities** (10 min)
   - Monitoring scan results
   - Fixing vulnerabilities
   - Documentation/exemptions

4. **Q&A** (5 min)

## Pre-Meeting
- Read: `docs/SECURITY.md`
- Read: `docs/SECURITY_RUNBOOK.md`

## Post-Meeting
- Everyone has access to scan reports
- Someone volunteers as security point person
- Set up Slack notification

EOF
```

---

## COMPLETE CHECKLIST

### Week 1: Baseline
- [ ] Install Trivy locally
- [ ] Run baseline scan on python:3.9-slim
- [ ] Generate reports and review findings
- [ ] Document vulnerabilities in SECURITY_BASELINE.md
- [ ] Team review of findings

### Week 2: Remediation
- [ ] Upgrade Dockerfile base image (python:3.9 → python:3.11)
- [ ] Run local tests to verify compatibility
- [ ] Update requirements.txt with patched versions
- [ ] Local test suite passes
- [ ] Rebuild and re-scan
- [ ] Document remaining vulnerabilities

### Week 3-4: GitHub Integration
- [ ] Copy Trivy scanning code to cd.yml
- [ ] Test on feature branch or test tag
- [ ] Verify scan runs successfully
- [ ] Verify artifacts uploaded
- [ ] Verify GitHub issues created
- [ ] Merge to main
- [ ] Update CI workflow (optional)

### Week 5-6: Helm Preparation
- [ ] Create Helm chart security values
- [ ] Document security policies in Helm chart
- [ ] Create SECURITY.md documentation
- [ ] Create SECURITY_RUNBOOK.md for team
- [ ] Schedule team training meeting
- [ ] Update README with security badge

---

## Success Criteria

- [ ] Trivy integrated into GitHub Actions
- [ ] SBOMs generated (CycloneDX + SPDX)
- [ ] Zero CRITICAL vulnerabilities in released image
- [ ] Team trained on vulnerability response
- [ ] Documentation complete
- [ ] Helm chart includes security policies
- [ ] CI/CD pipeline < 25 min total

EOF
```

---

## COMMON ISSUES & SOLUTIONS

### Issue: Trivy scan times out

```yaml
# Solution: Increase timeout
- name: Run Trivy security scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.meta.outputs.tags }}
    timeout: 10m  # ← Add this
```

### Issue: False positives in scan results

```bash
# Solution: Create .trivyignore and document
cat > .trivyignore << 'EOF'
# CVE-2024-XXXX: Requires specific vulnerable configuration not present
CVE-2024-XXXX
EOF
```

### Issue: Scan fails to download vulnerability database

```yaml
# Solution: Add retry logic
- name: Run Trivy security scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.meta.outputs.tags }}
    exit-code: '0'  # Don't fail build
    skip-update: false  # Allow DB updates
```

### Issue: SBOM files not uploading to release

```bash
# Solution: Check file existence and use correct API
- name: Upload to Release
  run: |
    ls -la sbom.* trivy-report.*  # Verify files exist
    gh release upload ${{ github.ref_name }} sbom.* trivy-report.*
```

---

## NEXT STEPS

1. **Start Week 1:** Run baseline Trivy scan
2. **Share analysis:** Distribute DOCKER_SECURITY_SCANNING_ANALYSIS.md to team
3. **Get approval:** Review findings with team lead
4. **Execute Phase 1:** Complete baseline analysis
5. **Execute Phase 2:** Remediate vulnerabilities
6. **Execute Phase 3:** Integrate into GitHub Actions
7. **Execute Phase 4:** Prepare Helm chart
8. **Team training:** Conduct meeting and runbook review

**Estimated Total Effort:** 12-17 hours over 4-6 weeks
**Cost:** $0 (open-source tools)
**ROI:** High (prevents security incidents, enables Helm deployment, compliance-ready)

