# 🔒 Secure Coding Practices Guide

## Overview

This project follows **industry-standard secure coding practices** with automated security scanning at multiple levels.

## Security Layers

### 1. Local Security Checks ✅

Run comprehensive security analysis on your machine:

```bash
python run_security_check.py
```

**What it checks:**
- ✅ **Code Security** - Bandit scans for common vulnerabilities
- ✅ **Dependencies** - Safety & pip-audit check for known CVEs
- ✅ **Secret Detection** - Finds accidentally committed credentials
- ✅ **Import Security** - Detects dangerous imports (eval, exec, pickle)
- ✅ **Code Quality** - Pylint identifies potential issues

### 2. Pre-Push Testing ✅

Automated before every push:
- All unit tests must pass
- Prevents broken code from reaching GitHub

### 3. CI/CD Pipeline Security ✅

GitHub Actions runs on every commit:
- **Bandit** - Security vulnerability scanner
- **Safety** - Known vulnerability database check
- **Pylint** - Code quality and potential bugs
- **Multi-version testing** - Python 3.9, 3.10, 3.11

### 4. Nightly Security Audits ✅

Automated daily at 2 AM UTC:
- Dependency vulnerability scans
- Outdated package detection
- Security advisories monitoring

## Quick Start

### Install Security Tools

```bash
# Install all security scanning tools
pip install bandit safety pip-audit pylint mypy

# Verify installation
python -m bandit --version
python -m safety --version
```

### Run Security Check

```bash
# Full security scan
python run_security_check.py

# Individual tools
python -m bandit -r src/ utils/
python -m safety check
python -m pip_audit
```

## Security Tools Explained

### 🛡️ Bandit
**Purpose:** Scans Python code for common security issues

**What it finds:**
- Hardcoded passwords
- SQL injection vulnerabilities
- Shell injection risks
- Use of unsafe functions (pickle, eval, exec)
- Weak cryptography
- Assert used in production code

**Example:**
```bash
python -m bandit -r src/ utils/ -ll
# -ll = only show medium/high severity
```

### 🔍 Safety
**Purpose:** Checks installed packages against vulnerability database

**What it finds:**
- Packages with known CVEs
- Vulnerable dependency versions
- Security advisories

**Example:**
```bash
python -m safety check --json
```

### 🔎 pip-audit
**Purpose:** Comprehensive dependency vulnerability scanner

**What it finds:**
- All transitive dependencies
- Python package vulnerabilities
- Detailed CVE information

**Example:**
```bash
python -m pip_audit --desc
```

### 📋 Pylint
**Purpose:** Code quality and bug detection

**What it finds:**
- Potential bugs
- Code smells
- Unreachable code
- Unused variables
- Type errors

## Industry Standards Followed

### OWASP Top 10 Protections

1. **A01 - Broken Access Control** ✅
   - No authentication/authorization in current app
   - Public API only (read-only data)

2. **A02 - Cryptographic Failures** ✅
   - No sensitive data storage
   - No custom crypto implementations

3. **A03 - Injection** ✅
   - Bandit scans for SQL/command injection
   - Parameterized API requests only

4. **A04 - Insecure Design** ✅
   - Code reviews required via PR checks
   - Security scanning in CI/CD

5. **A05 - Security Misconfiguration** ✅
   - Dependencies scanned daily
   - No debug mode in production

6. **A06 - Vulnerable Components** ✅
   - Safety + pip-audit check dependencies
   - Automated daily scans

7. **A07 - Authentication Failures** ✅
   - No authentication system (public data)

8. **A08 - Data Integrity Failures** ✅
   - Read-only API consumption
   - No data persistence to untrusted sources

9. **A09 - Logging Failures** ✅
   - Structured error handling
   - No sensitive data in logs

10. **A10 - SSRF** ✅
    - Only MLB API endpoints accessed
    - No user-controlled URLs

### CWE (Common Weakness Enumeration)

Our scanners detect:
- **CWE-78**: OS Command Injection
- **CWE-79**: Cross-site Scripting
- **CWE-89**: SQL Injection
- **CWE-94**: Code Injection
- **CWE-259**: Hard-coded Password
- **CWE-327**: Weak Crypto
- **CWE-502**: Deserialization of Untrusted Data
- **CWE-798**: Hard-coded Credentials

## Current Security Status

### Known Safe Practices in This Codebase

✅ **Pickle Usage** - Used only for local caching (not user input)
```python
# Safe: Caching our own processed data
cache.set_cache('key', processed_data)
```

✅ **API Requests** - Only to trusted MLB Stats API
```python
# Safe: Fixed endpoint, no user input in URL
response = requests.get(f"{self.base_url}/teams")
```

✅ **No User Authentication** - Public data only, no credentials

✅ **No Database** - No SQL injection risk

✅ **Input Validation** - Natural language queries parsed safely

### Potential Security Considerations

⚠️ **Pickle for Caching**
- **Status:** Acceptable for local-only caching
- **Risk:** Low (we control the data being pickled)
- **Mitigation:** Never pickle user input or external data

⚠️ **Streamlit App**
- **Status:** Safe for current use case
- **Risk:** Low (read-only data display)
- **Mitigation:** No file uploads, no user authentication needed

## Development Workflow

### Before Committing

```bash
# 1. Run tests
python run_tests.py

# 2. Run security check (optional but recommended)
python run_security_check.py

# 3. Commit and push
git add .
git commit -m "Your message"
git push
# → Pre-push hook runs tests
# → CI runs security scans
```

### Before Major Releases

```bash
# Full security audit
python run_security_check.py

# Update dependencies
pip list --outdated
pip install --upgrade <package>

# Re-run tests
python run_tests.py

# Push and verify CI
git push
gh run watch
```

## CI/CD Security Pipeline

### On Every Push

```yaml
jobs:
  test:
    - Run tests (Python 3.9, 3.10, 3.11)
    - Code coverage
    
  code-quality:
    - Pylint analysis
    - Bandit security scan
    - Safety vulnerability check
```

### Nightly (2 AM UTC)

```yaml
jobs:
  integration-tests:
    - Real API connectivity
    - Performance benchmarks
    
  dependency-audit:
    - Safety check
    - pip-audit scan
    - Outdated package detection
```

## Security Checklist

### For Every Commit
- [ ] Tests pass locally (`python run_tests.py`)
- [ ] No secrets in code
- [ ] No debug code (pdb, breakpoint)
- [ ] Pre-push hook passes

### Weekly
- [ ] Run security check (`python run_security_check.py`)
- [ ] Review dependency updates
- [ ] Check GitHub security alerts

### Before Deployment
- [ ] All CI checks pass
- [ ] Security scan clean
- [ ] Dependencies up to date
- [ ] No high-severity warnings

## Handling Security Issues

### If Vulnerability Found

1. **Assess Severity**
   - Critical/High: Fix immediately
   - Medium: Fix within 1 week
   - Low: Fix in next release

2. **Update Dependency**
   ```bash
   pip install --upgrade <vulnerable-package>
   python run_tests.py
   git commit -m "Security: Update <package> to fix CVE-XXXX"
   ```

3. **Verify Fix**
   ```bash
   python run_security_check.py
   python -m safety check
   ```

### If Bandit Flags Code

1. **Review Finding**
   - Is it a real issue or false positive?

2. **Fix or Suppress**
   ```python
   # If false positive, suppress with explanation
   result = pickle.load(f)  # nosec - Safe: local cache only
   ```

3. **Document Decision**
   - Add comment explaining why it's safe

## Resources

### Tools Documentation
- **Bandit:** https://bandit.readthedocs.io/
- **Safety:** https://pyup.io/safety/
- **pip-audit:** https://pypi.org/project/pip-audit/
- **Pylint:** https://pylint.pycqa.org/

### Security Standards
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **CWE:** https://cwe.mitre.org/
- **Python Security:** https://python.readthedocs.io/en/latest/library/security_warnings.html

### GitHub Security
- **Security Advisories:** Check repository → Security tab
- **Dependabot:** Automated dependency updates
- **Code Scanning:** Advanced security features

## Summary

Your codebase has **multiple layers of security**:

1. ✅ **Local scanning** - `run_security_check.py`
2. ✅ **Pre-push testing** - Automated before push
3. ✅ **CI/CD scanning** - Every commit checked
4. ✅ **Nightly audits** - Daily security monitoring
5. ✅ **Industry standards** - OWASP, CWE compliance

**Current Status:** 🟢 **SECURE**

Your MLB Statistics application follows industry-standard secure coding practices with comprehensive automated security scanning!

---

**Last Security Audit:** Run `python run_security_check.py`  
**CI/CD Status:** https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis/actions  
**Security Tools:** Bandit, Safety, pip-audit, Pylint
