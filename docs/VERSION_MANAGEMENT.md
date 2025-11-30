# Version Management

This project uses automated version incrementing based on successful test execution.

## How It Works

### Automatic Versioning
When code is pushed to `master` or `main` branch:

1. **Trigger**: GitHub Actions workflow detects changes in source files
2. **Test**: Full regression test suite runs automatically
3. **Increment**: If all tests pass, version is auto-incremented
4. **Commit**: Version changes are committed back to repository
5. **Tag**: A git tag is created (e.g., `v1.0.1`)

### Version Format

We use [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes (manual increment)
- **MINOR**: New features, backward compatible (manual increment)  
- **PATCH**: Bug fixes, automated increment ✨

**Example**: `1.0.0` → `1.0.1` → `1.0.2` (automatic)

### Files Updated

When version is bumped, these files are automatically updated:

1. `src/__init__.py` - Python version constant
2. `pyproject.toml` - Package metadata version
3. `CHANGELOG.md` - Version history entry

### Manual Version Increment

To manually increment version (for MAJOR or MINOR changes):

```bash
# From project root
python scripts/bump_version.py
```

Or edit these files directly:
- `src/__init__.py`: `__version__ = "X.Y.Z"`
- `pyproject.toml`: `version = "X.Y.Z"`

### Testing Locally

Test the version bump script before pushing:

```bash
# See what would change (dry run)
python scripts/bump_version.py

# Check current version
python -c "from src import __version__; print(__version__)"
```

### Viewing Version History

```bash
# View all version tags
git tag -l "v*"

# View version history
git log --oneline --grep="bump version"

# View changelog
cat CHANGELOG.md
```

### CI/CD Integration

The auto-versioning workflow (`.github/workflows/auto-version.yml`):

- ✅ Runs on push to `master`/`main`
- ✅ Only triggers on source code changes
- ✅ Prevents infinite loops with `[auto-version]` marker
- ✅ Creates git tags for releases
- ✅ Updates changelog automatically
- ✅ Only increments if ALL tests pass

### Workflow Triggers

Version bump runs when these paths change:
- `src/**` - Source code
- `utils/**` - Utility modules
- `streamlit_app.py` - Main application
- `requirements.txt` - Dependencies
- `pyproject.toml` - Project config

### Skip Auto-versioning

To push changes WITHOUT triggering version bump:

```bash
# Include [skip ci] in commit message
git commit -m "docs: update README [skip ci]"
```

Or modify non-triggering files:
- Documentation (`.md` files)
- Tests (`tests/**`)
- Config files (`.github/`, `.gitignore`)

### Version Display

Current version is displayed in:
- **Streamlit UI**: Top of sidebar (`v1.0.0`)
- **Python code**: `from src import __version__`
- **Package metadata**: `pyproject.toml`

### Troubleshooting

**Version didn't increment?**
- Check if tests passed: GitHub Actions → Auto Version Bump
- Verify changes were in trigger paths
- Check for `[skip ci]` in commit message

**Need to revert version?**
```bash
# Revert to specific version
git checkout v1.0.5 -- src/__init__.py pyproject.toml

# Or manually edit files
```

**Force version bump?**
```bash
# Run script manually
python scripts/bump_version.py

# Commit and push
git add src/__init__.py pyproject.toml CHANGELOG.md
git commit -m "chore: manual version bump [auto-version]"
git push
```

## Best Practices

1. **Let it auto-increment**: Don't manually change PATCH version
2. **Update MAJOR/MINOR manually**: Use `bump_version.py` or edit files
3. **Keep tests green**: Version only increments on passing tests
4. **Use tags**: Reference specific versions with `v1.0.5` tags
5. **Check CHANGELOG**: Review what changed between versions

## Example Workflow

```bash
# 1. Make changes
vim src/data_fetcher.py

# 2. Commit and push
git add .
git commit -m "fix: improve error handling"
git push origin master

# 3. GitHub Actions runs:
#    - Tests execute
#    - Version bumps (1.0.0 → 1.0.1)
#    - Tag created (v1.0.1)
#    - Changes committed

# 4. Pull latest
git pull

# 5. Verify version
python -c "from src import __version__; print(__version__)"
# Output: 1.0.1
```

## Benefits

✅ **Consistent**: Every commit has unique version  
✅ **Traceable**: Git tags track all releases  
✅ **Automated**: No manual version management  
✅ **Safe**: Only increments on passing tests  
✅ **Auditable**: CHANGELOG tracks all changes  
✅ **Professional**: Industry-standard versioning
