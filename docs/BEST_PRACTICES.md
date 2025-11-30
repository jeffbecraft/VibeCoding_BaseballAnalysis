# Industry Best Practices Implementation Guide

This document explains the industry best practices that have been implemented in the MLB Statistics Analysis System.

## Table of Contents

1. [Structured Logging](#1-structured-logging)
2. [Environment Configuration](#2-environment-configuration)
3. [Modern Package Management](#3-modern-package-management)
4. [Dependency Version Pinning](#4-dependency-version-pinning)
5. [API Rate Limiting & Retry Logic](#5-api-rate-limiting--retry-logic)
6. [Pre-commit Hooks](#6-pre-commit-hooks)
7. [Health Check Monitoring](#7-health-check-monitoring)

---

## 1. Structured Logging

### What Changed
Replaced all `print()` statements with Python's `logging` module for professional logging.

### Benefits
- **Configurable log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Timestamps**: Every log has a timestamp
- **Context**: Know which module generated the log
- **File logging**: Can log to files for production monitoring
- **Easy to disable**: Set `LOG_LEVEL=ERROR` to hide debug messages

### How to Use

```python
from src.logger import get_logger

# Create logger for your module
logger = get_logger(__name__)

# Log at different levels
logger.debug("Detailed debugging information")
logger.info("General information about program flow")
logger.warning("Something unexpected happened")
logger.error("An error occurred", exc_info=True)  # Includes stack trace
logger.critical("Critical failure!")
```

### Configuration

Set log level via environment variable:
```bash
# In .env file
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Or programmatically:
```python
from src.logger import set_log_level
set_log_level('DEBUG')  # Enable verbose debugging
```

### Output Example
```
2025-11-30 14:30:55 - mlb_stats.api - INFO - API Request: people/592450
2025-11-30 14:30:56 - mlb_stats.api - INFO - API Response: people/592450 (0.95s)
2025-11-30 14:30:56 - mlb_stats.cache - DEBUG - Cached response for: people/592450
```

---

## 2. Environment Configuration

### What Changed
Added `.env` file support for configuration management using `python-dotenv`.

### Benefits
- **Secrets not in code**: API keys, tokens stay out of version control
- **Environment-specific**: Different settings for dev/staging/production
- **Easy deployment**: Just change .env file, no code changes
- **Centralized config**: All settings in one place

### Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your configuration:**
   ```ini
   # AI Configuration
   OPENAI_API_KEY=your_actual_key_here
   AI_PROVIDER=auto
   AI_MODEL=llama3.2
   
   # Application
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   ```

3. **Never commit .env to Git** (already in .gitignore)

### Available Settings

See `.env.example` for all options. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | INFO | Logging verbosity |
| `AI_PROVIDER` | auto | AI provider (auto/ollama/openai) |
| `AI_MODEL` | llama3.2 | AI model name |
| `OPENAI_API_KEY` | - | OpenAI API key (if using OpenAI) |
| `CACHE_TTL_HOURS` | 24 | Cache refresh time |
| `API_TIMEOUT_SECONDS` | 10 | Request timeout |
| `ENVIRONMENT` | development | Environment name |

### How It Works

Configuration is automatically loaded at application start:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

# Access configuration
api_key = os.getenv('OPENAI_API_KEY')
log_level = os.getenv('LOG_LEVEL', 'INFO')  # Default to INFO
```

---

## 3. Modern Package Management

### What Changed
Added `pyproject.toml` - the modern Python packaging standard (PEP 518).

### Benefits
- **Single source of truth**: All project metadata in one file
- **Better dependency resolution**: Modern package managers use this
- **Tool configuration**: Black, pytest, mypy configs in one file
- **Optional dependencies**: Separate dev/web/notebook packages
- **Future-proof**: Industry standard going forward

### Structure

```toml
[project]
name = "mlb-stats-analysis"
version = "1.0.0"
dependencies = [
    "pandas>=2.0.0,<3.0.0",
    "requests>=2.31.0,<3.0.0",
    # Core dependencies
]

[project.optional-dependencies]
dev = ["pytest>=7.4.0", "black>=23.0.0"]  # Development tools
web = ["streamlit>=1.28.0", "plotly>=5.17.0"]  # Web app
all = ["mlb-stats-analysis[dev,web,notebooks,ai]"]  # Everything

[tool.black]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Installation Options

```bash
# Core dependencies only
pip install -e .

# With web app
pip install -e ".[web]"

# Development setup (includes testing tools)
pip install -e ".[dev]"

# Everything
pip install -e ".[all]"
```

### Tool Configuration

Tools now read config from `pyproject.toml`:
- **Black**: Line length 100, Python 3.9+
- **Pytest**: Auto-discover tests, coverage reports
- **MyPy**: Type checking settings
- **Flake8**: Linting rules

---

## 4. Dependency Version Pinning

### What Changed
Created `requirements.lock` with exact versions for reproducible builds.

### Benefits
- **Reproducible builds**: Same versions every time
- **Prevents breaking changes**: New package versions won't surprise you
- **Easy rollback**: Know exactly what changed
- **CI/CD friendly**: Consistent test environments

### Usage

**For development** (flexible versions):
```bash
pip install -r requirements.txt
```

**For production** (exact versions):
```bash
pip install -r requirements.lock
```

### Updating Lock File

When you add/update dependencies:
```bash
pip install -r requirements.txt  # Install latest compatible
pip freeze > requirements.lock   # Lock current versions
```

### Version Ranges

In `requirements.txt`:
```
pandas>=2.0.0,<3.0.0  # Any 2.x version
requests>=2.31.0      # 2.31.0 or higher
```

In `requirements.lock`:
```
pandas==2.1.4         # Exactly this version
requests==2.31.0      # Exactly this version
```

---

## 5. API Rate Limiting & Retry Logic

### What Changed
Implemented automatic retry logic using the `tenacity` library.

### Benefits
- **Resilience**: Automatic retry for transient failures
- **Prevents API bans**: Smart backoff prevents hammering APIs
- **Better user experience**: Temporary issues don't fail queries
- **Configurable**: Timeout and retry settings via environment

### How It Works

Retry logic with exponential backoff:

```python
@retry(
    stop=stop_after_attempt(3),  # Try up to 3 times
    wait=wait_exponential(multiplier=1, min=1, max=10),  # 1s, 2s, 4s, ...
    retry=retry_if_exception_type((Timeout, ConnectionError))
)
def _make_api_request_with_retry(self, url, params):
    response = requests.get(url, params=params, timeout=self.timeout)
    # ...
```

### Retry Behavior

| Attempt | Wait Time | What Happens |
|---------|-----------|--------------|
| 1 | 0s | Immediate first try |
| 2 | 1s | Wait 1 second, retry |
| 3 | 2s | Wait 2 seconds, retry |
| 4 | 4s | Wait 4 seconds, final retry |
| Fail | - | Return error after 3 retries |

### Configuration

```ini
# In .env
API_TIMEOUT_SECONDS=10  # How long to wait for response
```

### Logged Output

```
2025-11-30 14:30:55 - mlb_stats.api - INFO - API Request: teams
2025-11-30 14:31:05 - mlb_stats.api - WARNING - Request timeout for .../teams: Timeout
2025-11-30 14:31:06 - mlb_stats.api - INFO - API Response: teams (1.05s)
```

---

## 6. Pre-commit Hooks

### What Changed
Added `.pre-commit-config.yaml` for automated code quality checks.

### Benefits
- **Catch errors early**: Before committing broken code
- **Consistent formatting**: Auto-format code with Black
- **Security**: Bandit checks for security issues
- **Team consistency**: Everyone follows same standards
- **Time saver**: Automated checks vs manual review

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks (one-time setup)
pre-commit install

# Optional: Run on all files now
pre-commit run --all-files
```

### What Gets Checked

Every time you `git commit`:

1. **Trailing whitespace**: Removed automatically
2. **End-of-file**: Ensures files end with newline
3. **YAML/JSON**: Validates syntax
4. **Large files**: Warns about files >1MB
5. **Black**: Auto-formats Python code
6. **isort**: Sorts imports
7. **flake8**: Lints Python code
8. **Bandit**: Checks security issues

### Example

```bash
$ git commit -m "Add new feature"

Trim Trailing Whitespace.................................................Passed
Fix End of Files.........................................................Passed
Check Yaml...............................................................Passed
Check JSON...............................................................Passed
Check for added large files..............................................Passed
black....................................................................Failed
- hook id: black
- files were modified by this tool

reformatted src/data_fetcher.py
1 file reformatted.

# Files are auto-fixed, try committing again
$ git add .
$ git commit -m "Add new feature"
[master abc1234] Add new feature
```

### Disable for One Commit

```bash
git commit --no-verify -m "Skip hooks"
```

---

## 7. Health Check Monitoring

### What Changed
Added system health monitoring to Streamlit sidebar.

### Benefits
- **Visibility**: See system status at a glance
- **Debugging**: Quick diagnosis of issues
- **Production monitoring**: Container orchestration support
- **Performance**: Cache hit rates, request counts

### What's Monitored

1. **Overall Status**
   - Healthy (all systems operational)
   - Degraded (some features unavailable)
   - Unhealthy (critical issues)

2. **Cache Statistics**
   - Hit rate percentage
   - Total requests
   - Cache enabled/disabled

3. **AI Availability**
   - Provider (Ollama/OpenAI)
   - Model name
   - Connection status

4. **Version Information**
   - Application version
   - Environment (dev/staging/production)

### Accessing Health Status

**In Streamlit UI:**
- Check sidebar → "🏥 System Health" section

**Programmatically:**
```python
from streamlit_app import get_health_status

health = get_health_status()
print(health)
# {
#   'status': 'healthy',
#   'cache': {'enabled': True, 'stats': {...}},
#   'ai': {'available': True, 'provider': 'ollama'},
#   'version': '1.0.0',
#   'environment': 'production'
# }
```

### For Container Orchestration

Perfect for Kubernetes liveness/readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8501
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

## Migration Checklist

For developers upgrading to the new best practices:

- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Copy environment template: `cp .env.example .env`
- [ ] Configure .env with your settings
- [ ] Update print statements to logger (optional but recommended)
- [ ] Install pre-commit hooks: `pip install pre-commit && pre-commit install`
- [ ] Run tests to verify: `python run_tests.py`
- [ ] Check health status in Streamlit sidebar

---

## Backward Compatibility

✅ **All changes are backward compatible!**

- Old code still works
- No breaking changes
- Gradual migration supported
- Default values provided for all new settings

---

## Questions?

See the main documentation:
- Architecture: `docs/ARCHITECTURE.md`
- Environment config: `.env.example`
- Package info: `pyproject.toml`
- Changelog: `CHANGELOG.md`
