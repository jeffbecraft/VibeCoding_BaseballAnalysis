# 🎴 Player Baseball Cards - Quick Guide

## What It Does

**Shows player photos** when you ask about specific players!

## Try It Now

Ask these questions:
- "Show me Aaron Judge's career stats"
- "What was Shohei Ohtani's batting average in 2024?"
- "Gunnar Henderson home runs"

## What You'll See

- Player photo (official MLB headshot)
- Name, number, position
- Team, height, weight, age
- Batting/throwing handedness

## How It Works

**Uses MLB.com's official image CDN**
- ✅ FREE (no API key)
- ✅ Always current
- ✅ High quality
- ✅ Automatic fallback if photo missing

## Quick Code Example

```python
from src.player_images import get_player_headshot_url

# Get Aaron Judge's headshot
url = get_player_headshot_url(592450, size='medium')
# Returns: https://img.mlbstatic.com/mlb-photos/.../592450/headshot/67/current
```

## Image Sizes

- **Small**: 120px (thumbnails)
- **Medium**: 213px (default) ⭐
- **Large**: 426px (high-res)

## About Topps Cards

**Q: Does Topps provide an API?**

**A: No.** Topps doesn't have a public API. We use MLB's official player headshots instead - they're free, current, and professional quality!

## Files Modified

- ✅ `src/player_images.py` - Image URL functions
- ✅ `streamlit_app.py` - Display integration
- ✅ `docs/PLAYER_IMAGES.md` - Full documentation

## Learn More

See `docs/PLAYER_IMAGES.md` for complete documentation!

---

**Version:** 1.1.0+  
**Status:** ✅ Ready to use!
