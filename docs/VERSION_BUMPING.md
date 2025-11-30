# Version Bumping Guide

This project uses **bump-my-version** for automated version management following Semantic Versioning (SemVer).

---

## 📋 Quick Reference

```bash
# Bug fix (1.1.0 → 1.1.1)
bump-my-version bump patch

# New feature (1.1.0 → 1.2.0)
bump-my-version bump minor

# Breaking change (1.1.0 → 2.0.0)
bump-my-version bump major
```

**What it does automatically:**
- ✅ Updates `src/__init__.py`
- ✅ Updates `pyproject.toml`
- ✅ Creates git commit
- ✅ Creates git tag (`v1.1.1`)
- ✅ Ready to push!

---

## 🎯 Semantic Versioning Rules

**Format:** `MAJOR.MINOR.PATCH`

| Type | When to Use | Example |
|------|-------------|---------|
| **PATCH** | Bug fixes, typos, minor changes | `1.1.0 → 1.1.1` |
| **MINOR** | New features (backward-compatible) | `1.1.0 → 1.2.0` |
| **MAJOR** | Breaking changes (incompatible) | `1.1.0 → 2.0.0` |

---

## 🚀 Step-by-Step Workflow

### 1. Make Your Changes
```bash
# Make code changes
git add .
git commit -m "feat: add new feature"
```

### 2. Bump Version
```bash
# Choose appropriate bump type
bump-my-version bump minor  # For new feature
```

**This automatically:**
- Updates version in `src/__init__.py` and `pyproject.toml`
- Creates commit: `chore: bump version to 1.2.0`
- Creates tag: `v1.2.0`

### 3. Push to GitHub
```bash
git push
git push --tags
```

**Result:**
- ✅ Version 1.2.0 deployed
- ✅ Git tag visible on GitHub
- ✅ Ready for release

---

## 📖 Detailed Examples

### Example 1: Bug Fix
```bash
# You fixed a bug
git add .
git commit -m "fix: correct email address validation"

# Bump patch version
bump-my-version bump patch
# 1.1.0 → 1.1.1

git push --follow-tags
```

### Example 2: New Feature
```bash
# You added GitHub issue reporting
git add .
git commit -m "feat: add automatic GitHub issue creation"

# Bump minor version
bump-my-version bump minor
# 1.1.0 → 1.2.0

git push --follow-tags
```

### Example 3: Breaking Change
```bash
# You removed old API
git add .
git commit -m "BREAKING CHANGE: remove deprecated stats API"

# Bump major version
bump-my-version bump major
# 1.1.0 → 2.0.0

git push --follow-tags
```

---

## 🔍 Preview Without Committing

```bash
# See what would change
bump-my-version bump --dry-run patch

# Output:
# New version: 1.1.1
# Would update: src/__init__.py
# Would update: pyproject.toml
# Would create commit: chore: bump version to 1.1.1
# Would create tag: v1.1.1
```

---

## ⚙️ Configuration

Configuration is in `.bumpversion.cfg`:

```ini
[bumpversion]
current_version = 1.1.0
commit = True              # Auto-commit changes
tag = True                 # Auto-create git tag
tag_name = v{new_version}  # Tag format: v1.2.0
message = chore: bump version to {new_version}

[bumpversion:file:src/__init__.py]
# Updates __version__ = "1.1.0"

[bumpversion:file:pyproject.toml]
# Updates version = "1.1.0"
```

---

## 🎨 Conventional Commits (Recommended)

Use consistent commit message format:

```bash
feat: add new feature          → Bump MINOR
fix: fix bug                   → Bump PATCH
docs: update documentation     → No bump (manually decide)
chore: update dependencies     → No bump (manually decide)
BREAKING CHANGE: remove API    → Bump MAJOR
```

**Examples:**
```bash
git commit -m "feat: add user authentication"
git commit -m "fix: resolve memory leak in cache"
git commit -m "docs: update README with examples"
git commit -m "chore: upgrade dependencies"
```

---

## 🛠️ Installation

Already included in `requirements.txt`:

```bash
# Install in virtual environment
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Verify installation
bump-my-version --version
```

---

## 📊 Version History

Current version tracking:
- **src/__init__.py**: `__version__ = "1.1.0"`
- **pyproject.toml**: `version = "1.1.0"`
- **Git tag**: `v1.1.0`

All three stay synchronized automatically!

---

## 🚨 Common Issues

### Issue: "No such file or directory"
**Solution:** Make sure you're in project root:
```bash
cd C:\VibeCoding_BaseballAnalysis
bump-my-version bump patch
```

### Issue: "Current version not found"
**Solution:** Update `.bumpversion.cfg` with current version:
```ini
current_version = 1.1.0  # Match src/__init__.py
```

### Issue: "Tag already exists"
**Solution:** Delete tag and try again:
```bash
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0
bump-my-version bump patch
```

---

## 🎯 Best Practices

### ✅ DO
- ✅ Bump version AFTER merging features
- ✅ Use `--dry-run` to preview changes
- ✅ Push tags immediately after bumping
- ✅ Use conventional commits for clarity
- ✅ Document breaking changes in commit messages

### ❌ DON'T
- ❌ Manually edit version numbers
- ❌ Forget to push tags
- ❌ Bump version for every small commit
- ❌ Skip patch bumps for bug fixes
- ❌ Use major bumps unless truly breaking

---

## 📝 Quick Commands Cheat Sheet

```bash
# Dry run (preview only)
bump-my-version bump --dry-run patch

# Bump patch (1.1.0 → 1.1.1)
bump-my-version bump patch

# Bump minor (1.1.0 → 1.2.0)
bump-my-version bump minor

# Bump major (1.1.0 → 2.0.0)
bump-my-version bump major

# Push everything
git push --follow-tags

# Check current version
git describe --tags
```

---

## 🔗 Resources

- **Semantic Versioning:** https://semver.org/
- **Bump-my-version Docs:** https://github.com/callowayproject/bump-my-version
- **Conventional Commits:** https://www.conventionalcommits.org/

---

**Now your versions stay synchronized automatically! 🎉**
