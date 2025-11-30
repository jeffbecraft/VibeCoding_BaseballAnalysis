# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for continuous integration and deployment. The pipeline ensures code quality, runs automated tests, and deploys the application to Streamlit Cloud.

## Pipeline Structure

### 1. CI Pipeline (`ci.yml`)

**Triggers:**
- Push to `master`, `main`, or `develop` branches
- Pull requests to `master` or `main`

**Jobs:**

#### Test Job
- **Matrix testing** across Python 3.9, 3.10, and 3.11
- Installs dependencies with pip caching
- Runs linting with flake8
- Checks code formatting with black
- Executes full test suite
- Generates coverage reports
- Uploads coverage to Codecov

#### Code Quality Job
- Runs pylint for code quality analysis
- Executes bandit for security scanning
- Checks dependencies for known vulnerabilities with safety

#### Build Test Job
- Validates Streamlit app can be compiled
- Checks configuration files are valid

**Status:** Runs on every push and PR

### 2. Deploy Pipeline (`deploy.yml`)

**Triggers:**
- Push to `master` or `main` branch
- Changes to: `streamlit_app.py`, `src/**`, `utils/**`, `requirements_web.txt`, `.streamlit/**`
- Manual trigger via workflow_dispatch

**Jobs:**

#### Deploy Job
- Validates Python environment
- Installs dependencies
- Runs full test suite before deployment
- Validates Streamlit app syntax
- Creates deployment marker with timestamp and commit info
- Prepares for automatic Streamlit Cloud deployment

**Status:** Streamlit Cloud auto-deploys from successful pushes to master

### 3. Nightly Tests (`nightly.yml`)

**Triggers:**
- Scheduled: Daily at 2 AM UTC
- Manual trigger via workflow_dispatch

**Jobs:**

#### Integration Tests
- Runs tests against real MLB API
- Tests API endpoint connectivity
- Validates data fetching functionality
- Performance benchmarking (cache vs no-cache)

#### Dependency Audit
- Scans for security vulnerabilities
- Checks for outdated packages
- Generates security reports

**Status:** Monitors ongoing system health

### 4. Pull Request Checks (`pr-check.yml`)

**Triggers:**
- PR opened, synchronized, or reopened

**Jobs:**

#### PR Validation
- Runs full test suite with coverage
- Checks if new tests were added
- Validates code changes
- Provides PR statistics
- Auto-comments on PR with status

**Status:** Required for PR approval

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer Workflow                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   Commit & Push      │
                   └──────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌─────────────────┐      ┌─────────────────┐
        │   Pull Request  │      │   Push to Main  │
        └─────────────────┘      └─────────────────┘
                 │                         │
                 ▼                         ▼
        ┌─────────────────┐      ┌─────────────────┐
        │  PR Validation  │      │   CI Pipeline   │
        │   - Tests       │      │   - Multi-ver   │
        │   - Coverage    │      │   - Linting     │
        │   - Stats       │      │   - Security    │
        └─────────────────┘      └─────────────────┘
                 │                         │
                 ▼                         ▼
        ┌─────────────────┐      ┌─────────────────┐
        │  Code Review    │      │  Deploy Check   │
        └─────────────────┘      └─────────────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                   ┌──────────────────────┐
                   │   Merge to Main      │
                   └──────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Auto-Deploy to      │
                   │  Streamlit Cloud     │
                   └──────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   Live Application   │
                   │   🌐 Public URL      │
                   └──────────────────────┘

        ┌─────────────────────────────────────┐
        │      Nightly Monitoring             │
        │   - Integration Tests (2 AM UTC)    │
        │   - Dependency Audits               │
        │   - Performance Benchmarks          │
        └─────────────────────────────────────┘
```

## Pipeline Features

### ✅ Automated Testing
- Unit tests for all components
- Integration tests with real API (nightly)
- Test coverage reporting
- Multi-version Python compatibility

### 🔒 Security
- Dependency vulnerability scanning
- Code security analysis with bandit
- Regular security audits
- Safe secrets management

### 📊 Code Quality
- Linting with flake8
- Code formatting with black
- Static analysis with pylint
- Complexity checking

### 🚀 Deployment
- Automatic deployment on merge
- Pre-deployment validation
- Rollback capability via git
- Zero-downtime updates

### 📈 Monitoring
- Daily integration tests
- Performance benchmarking
- Dependency health checks
- Build status notifications

## Configuration Files

### GitHub Actions Workflows
- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/deploy.yml` - Deployment automation
- `.github/workflows/nightly.yml` - Scheduled tests
- `.github/workflows/pr-check.yml` - PR validation

### Required Secrets
No secrets required for current setup. All operations use public APIs and services.

### Optional: Codecov Integration
To enable code coverage tracking:
1. Sign up at https://codecov.io/
2. Add repository
3. Add `CODECOV_TOKEN` to GitHub repository secrets

## Local Testing

Test the pipeline locally before pushing:

```bash
# Run tests
python run_tests.py

# Check code quality
pip install flake8 black pylint
flake8 src/ utils/
black --check .
pylint src/ utils/

# Test Streamlit app
python -m py_compile streamlit_app.py
```

## Deployment Process

### Automatic Deployment (Recommended)
1. Push changes to `master` branch
2. CI pipeline runs automatically
3. All tests must pass
4. Streamlit Cloud deploys automatically
5. Monitor deployment at https://share.streamlit.io/

### Manual Deployment
1. Go to GitHub Actions tab
2. Select "Deploy to Streamlit Cloud" workflow
3. Click "Run workflow"
4. Select branch (usually `master`)
5. Click "Run workflow" button

## Monitoring & Logs

### View Pipeline Status
- GitHub repository → Actions tab
- See all workflow runs and their status
- Click on any run for detailed logs

### Streamlit Cloud Logs
- https://share.streamlit.io/
- Select your app
- View "Logs" tab for runtime errors

### Build Badges
Add to README.md:
```markdown
![CI](https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis/workflows/CI%20Pipeline/badge.svg)
![Deploy](https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis/workflows/Deploy%20to%20Streamlit%20Cloud/badge.svg)
```

## Troubleshooting

### Tests Fail in CI but Pass Locally
- Check Python version compatibility
- Verify all dependencies in requirements.txt
- Check for environment-specific code

### Deployment Fails
- Check Streamlit Cloud logs
- Verify requirements_web.txt is complete
- Ensure no syntax errors in streamlit_app.py

### Integration Tests Fail
- MLB API might be down or rate-limited
- Check internet connectivity in CI
- Review nightly test logs

## Best Practices

1. **Always run tests locally** before pushing
2. **Keep dependencies updated** to avoid security issues
3. **Write tests for new features** to maintain coverage
4. **Review CI logs** after every push
5. **Monitor nightly tests** for API changes

## Future Enhancements

Potential additions to the pipeline:
- [ ] Docker containerization
- [ ] Blue-green deployment
- [ ] A/B testing framework
- [ ] Performance regression testing
- [ ] Automated release notes
- [ ] Slack/Discord notifications
- [ ] Database migration automation
- [ ] Load testing

## Support

For issues with the CI/CD pipeline:
1. Check GitHub Actions logs
2. Review this documentation
3. Open an issue on GitHub
4. Contact the maintainer

---

**Last Updated:** November 30, 2025  
**Maintained By:** MLB Stats Team  
**Pipeline Version:** 1.0
