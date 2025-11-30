# 🚀 Quick Version Bump Guide

**Current Version:** 1.1.0

---

## 📋 Commands

```bash
# See what would happen (no changes)
bump-my-version show-bump

# Bug fix (1.1.0 → 1.1.1)
bump-my-version bump patch

# New feature (1.1.0 → 1.2.0)
bump-my-version bump minor

# Breaking change (1.1.0 → 2.0.0)
bump-my-version bump major

# Push changes
git push --follow-tags
```

---

## ✅ What Happens Automatically

When you run `bump-my-version bump patch`:

1. ✅ Updates `src/__init__.py` → `__version__ = "1.1.1"`
2. ✅ Updates `pyproject.toml` → `version = "1.1.1"`
3. ✅ Creates commit → `chore: bump version to 1.1.1`
4. ✅ Creates tag → `v1.1.1`
5. ✅ Ready to push!

---

## 📖 Full Documentation

See **[docs/VERSION_BUMPING.md](docs/VERSION_BUMPING.md)** for complete guide.

---

**That's it! No manual version editing needed! 🎉**
