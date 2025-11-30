# Automatic Version Management Implementation

## Overview
Implemented a complete automatic version management system that increments the build version every time code is committed to GitHub and passes the full regression test suite.

## Components Created

### 1. Version Bump Script (`scripts/bump_version.py`)
**Purpose**: Automatically increment version numbers and update project files

**Features**:
- Reads current version from `src/__init__.py`
- Increments PATCH version (e.g., 1.0.0 → 1.0.1)
- Updates version in multiple files simultaneously
- Adds entries to CHANGELOG.md
- Uses semantic versioning (MAJOR.MINOR.PATCH)

**Usage**:
```bash
python scripts/bump_version.py
```

**Files Updated by Script**:
- `src/__init__.py` - Python version constant
- `pyproject.toml` - Package metadata
- `CHANGELOG.md` - Version history

### 2. GitHub Actions Workflow (`.github/workflows/auto-version.yml`)
**Purpose**: Automate version bumping on successful CI/CD pipeline execution

**Workflow Steps**:
1. **Checkout**: Get latest code
2. **Setup**: Install Python 3.11 and dependencies
3. **Test**: Run full regression test suite (`python run_tests.py`)
4. **Bump**: If tests pass, increment version
5. **Commit**: Commit version changes back to repository
6. **Tag**: Create git tag (e.g., `v1.0.1`)
7. **Push**: Push changes and tag to GitHub

**Triggers**:
- Push to `master` or `main` branch
- Changes in source paths:
  - `src/**`
  - `utils/**`
  - `streamlit_app.py`
  - `requirements.txt`
  - `pyproject.toml`

**Safety Features**:
- Only runs if commit message doesn't contain `[auto-version]` (prevents loops)
- Only increments if ALL tests pass
- Creates annotated git tags for tracking
- Generates test report in GitHub UI

### 3. Documentation (`docs/VERSION_MANAGEMENT.md`)
**Purpose**: Comprehensive guide for understanding and using the versioning system

**Sections**:
- How automatic versioning works
- Version format explanation (semantic versioning)
- Files that get updated
- Manual version increment instructions
- Testing locally
- Viewing version history
- CI/CD integration details
- Workflow triggers
- Skipping auto-versioning
- Version display locations
- Troubleshooting guide
- Best practices
- Example workflow

## Version Format

Uses [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
  1  .  0  .  0
```

- **MAJOR**: Incompatible API changes (manual)
- **MINOR**: New features, backward compatible (manual)
- **PATCH**: Bug fixes, automated ✨

## How It Works

### Normal Development Workflow

```mermaid
graph TD
    A[Developer makes changes] --> B[Commit & push to master]
    B --> C{GitHub Actions triggered?}
    C -->|Yes, source files changed| D[Run full test suite]
    C -->|No, docs only| Z[Skip versioning]
    D --> E{All tests pass?}
    E -->|Yes| F[Bump PATCH version]
    E -->|No| G[Fail workflow, no version change]
    F --> H[Update files: __init__.py, pyproject.toml, CHANGELOG.md]
    H --> I[Commit with [auto-version] marker]
    I --> J[Create git tag v1.0.X]
    J --> K[Push to GitHub]
    K --> L[Developer pulls changes]
```

### Example Timeline

```
1. Developer: Fixes bug in data_fetcher.py
   Commit: "fix: handle API timeout error"
   Version: 1.0.0
   
2. GitHub Actions:
   - Runs 54 tests
   - All pass ✓
   - Bumps version to 1.0.1
   - Creates tag v1.0.1
   - Commits: "chore: bump version to 1.0.1 [auto-version]"
   
3. Developer: Adds new feature
   Commit: "feat: add player career stats"
   Version: 1.0.1
   
4. GitHub Actions:
   - Runs 54 tests
   - All pass ✓
   - Bumps version to 1.0.2
   - Creates tag v1.0.2
   - Commits: "chore: bump version to 1.0.2 [auto-version]"
```

## Version Display

Version is displayed in:

1. **Streamlit UI** (Top of sidebar)
   ```
   ⚾ MLB Stats Analysis v1.0.0
   Environment: production
   ```

2. **Python Code**
   ```python
   from src import __version__
   print(__version__)  # "1.0.0"
   ```

3. **Package Metadata**
   ```toml
   [project]
   name = "mlb-stats-analysis"
   version = "1.0.0"
   ```

4. **Git Tags**
   ```bash
   git tag -l "v*"
   # v1.0.0
   # v1.0.1
   # v1.0.2
   ```

## Manual Version Changes

For MAJOR or MINOR version bumps:

### Option 1: Use the Script
```bash
# Edit script to increment MAJOR or MINOR instead of PATCH
# Then run:
python scripts/bump_version.py
```

### Option 2: Edit Files Directly
```python
# src/__init__.py
__version__ = "2.0.0"  # or "1.1.0"

# pyproject.toml
version = "2.0.0"  # match __init__.py
```

Then commit:
```bash
git add src/__init__.py pyproject.toml
git commit -m "chore: bump to v2.0.0 - breaking changes [auto-version]"
git push
```

## Skip Auto-Versioning

### Method 1: Use [skip ci] in Commit
```bash
git commit -m "docs: update README [skip ci]"
```

### Method 2: Modify Non-Triggering Files
These paths don't trigger versioning:
- `docs/**`
- `tests/**`
- `.github/**` (except workflows)
- `*.md` files
- `.gitignore`, `.env.example`, etc.

## Testing Locally

Before pushing to GitHub:

```bash
# 1. Check current version
python -c "from src import __version__; print(__version__)"

# 2. Test bump script
python scripts/bump_version.py

# 3. Verify changes
python -c "from src import __version__; print(__version__)"
git diff src/__init__.py pyproject.toml CHANGELOG.md

# 4. Revert if needed (before committing)
git checkout src/__init__.py pyproject.toml CHANGELOG.md
```

## Benefits

✅ **Traceability**: Every build has unique version number  
✅ **Automation**: No manual version management needed  
✅ **Quality Gate**: Only increments on passing tests  
✅ **Git Integration**: Automatic tags for releases  
✅ **Audit Trail**: CHANGELOG tracks all versions  
✅ **Professional**: Industry-standard semantic versioning  
✅ **Visibility**: Version displayed in UI  
✅ **Rollback**: Easy to revert via git tags

## Troubleshooting

### Version Didn't Increment
**Check**:
1. Did tests pass? (GitHub Actions → Auto Version Bump)
2. Were source files modified? (not just docs)
3. Did commit have `[skip ci]`?

**Solution**: Check GitHub Actions logs for details

### Need to Revert Version
```bash
# Option 1: Revert to specific tag
git checkout v1.0.5 -- src/__init__.py pyproject.toml

# Option 2: Manual edit
# Edit src/__init__.py and pyproject.toml
git add src/__init__.py pyproject.toml
git commit -m "chore: revert version to 1.0.5"
```

### Force Version Bump
```bash
python scripts/bump_version.py
git add src/__init__.py pyproject.toml CHANGELOG.md
git commit -m "chore: manual version bump [auto-version]"
git push
```

## Files Modified

### New Files
1. `scripts/bump_version.py` - Version increment script
2. `.github/workflows/auto-version.yml` - GitHub Actions workflow
3. `docs/VERSION_MANAGEMENT.md` - User documentation
4. `docs/AUTO_VERSION_SUMMARY.md` - This file

### Modified Files
1. `README.md` - Added auto-versioning section
2. `streamlit_app.py` - Version display in sidebar (already done)
3. `src/__init__.py` - Version constant (will auto-update)
4. `pyproject.toml` - Version metadata (will auto-update)

## Next Steps

### Immediate
1. ✅ Commit these changes to trigger first auto-version
2. ✅ Verify GitHub Actions workflow runs successfully
3. ✅ Check that version increments to 1.0.1
4. ✅ Verify git tag v1.0.1 is created

### Future
- Monitor CHANGELOG.md for version history
- Use git tags for releases
- Reference versions in bug reports
- Track version in deployment logs

## Example Git Log

After implementation:
```
* abc1234 (tag: v1.0.2) chore: bump version to 1.0.2 [auto-version]
* def5678 feat: add comparison feature
* ghi9012 (tag: v1.0.1) chore: bump version to 1.0.1 [auto-version]
* jkl3456 fix: handle API timeout
* mno7890 (tag: v1.0.0) feat: implement auto-versioning
```

## Conclusion

The automatic version management system provides:
- **Zero manual effort** for PATCH version increments
- **Quality assurance** via test gate
- **Complete traceability** via git tags
- **Professional workflow** aligned with industry standards

Every successful commit to master now automatically gets a unique version number, ensuring proper version control and making it easy to track which code is running in any environment.
