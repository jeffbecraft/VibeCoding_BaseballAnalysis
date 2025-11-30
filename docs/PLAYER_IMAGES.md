# Player Baseball Card Images

## Overview

The MLB Statistics app now displays official player headshot images (baseball cards) when you ask about specific players! This feature uses MLB.com's official image CDN to show current player photos.

## ✨ What Just Happened?

Your app now automatically shows player "baseball cards" with photos and information when you ask about individual players.

**No API key needed!** These images are publicly available from MLB.com.

## 🎯 How It Works

### When Player Cards Appear

Player cards are automatically displayed when you query about specific players:

1. **Career Stats Queries**
   - "Show me Aaron Judge's career stats"
   - "What are Shohei Ohtani's career home runs?"
   - "Gunnar Henderson career statistics"

2. **Single Player Stats**
   - "What was Aaron Judge's batting average in 2024?"
   - "How many strikeouts did Gerrit Cole have in 2024?"

3. **Player Rankings**
   - "Where does Aaron Judge rank in home runs?"
   - "Rank Shohei Ohtani's stolen bases"

### What You See

When a player card displays, you'll see:

- **Player Photo** - Official MLB headshot
- **Full Name** - Player's complete name
- **Jersey Number** - Current uniform number
- **Position** - Primary playing position
- **Team** - Current team
- **Bats/Throws** - Batting and throwing handedness
- **Height/Weight** - Physical measurements
- **Age** - Current age

## 📸 Image Sources

### MLB.com Cloudinary CDN

All images come from MLB's official Cloudinary CDN:
- **Free to use** - No authentication required
- **Always current** - Updated automatically by MLB
- **High quality** - Multiple size options available
- **Fallback included** - Generic placeholder if player photo unavailable

### URL Pattern

```
https://img.mlbstatic.com/mlb-photos/image/upload/
    d_people:generic:headshot:67:current.png/  # Fallback image
    w_213,q_auto:best/                         # Size & quality
    v1/people/{player_id}/headshot/67/current  # Player specific
```

## 🎨 Image Sizes

Three size options are available:

| Size | Width | Use Case |
|------|-------|----------|
| Small | 120px | Thumbnails, compact lists |
| Medium | 213px | Default display (recommended) |
| Large | 426px | High-resolution, detailed view |

## 💻 For Developers

### Using in Your Code

```python
from src.player_images import get_player_headshot_url, display_player_card_streamlit
from src.data_fetcher import MLBDataFetcher

# Get a player's headshot URL
player_id = 592450  # Aaron Judge
url = get_player_headshot_url(player_id, size='medium')
print(url)

# In Streamlit app
fetcher = MLBDataFetcher()
players = fetcher.search_players("Aaron Judge")

if players:
    # Display full player card with info
    display_player_card_streamlit(players[0], size='medium', show_info=True)
```

### Available Functions

#### `get_player_headshot_url(player_id, size='medium')`

Generate URL for player headshot image.

**Parameters:**
- `player_id` (int): MLB player ID (e.g., 592450 for Aaron Judge)
- `size` (str): 'small', 'medium', or 'large'

**Returns:** URL string

**Example:**
```python
url = get_player_headshot_url(592450, 'large')
# Returns: https://img.mlbstatic.com/mlb-photos/.../592450/headshot/67/current
```

#### `get_player_action_shot_url(player_id, size='medium')`

Generate URL for player action shot (dynamic pose).

**Parameters:**
- `player_id` (int): MLB player ID
- `size` (str): 'small' (180px), 'medium' (360px), or 'large' (720px)

**Returns:** URL string

**Note:** Not all players have action shots. Falls back to generic placeholder.

#### `get_team_logo_url(team_id, style='light')`

Generate URL for team logo.

**Parameters:**
- `team_id` (int): MLB team ID (e.g., 147 for Yankees)
- `style` (str): 'light' (for dark backgrounds) or 'dark' (for light backgrounds)

**Returns:** URL string (SVG format)

**Example:**
```python
url = get_team_logo_url(147, 'light')
# Returns: https://www.mlbstatic.com/team-logos/team-cap-on-light/147.svg
```

#### `display_player_card_streamlit(player_data, size='medium', show_info=True)`

Display player card in Streamlit with photo and information.

**Parameters:**
- `player_data` (dict): Player dictionary from MLBDataFetcher (must have 'id' and 'fullName')
- `size` (str): Image size
- `show_info` (bool): Whether to show additional player info

**Example:**
```python
import streamlit as st
from src.data_fetcher import MLBDataFetcher
from src.player_images import display_player_card_streamlit

fetcher = MLBDataFetcher()
players = fetcher.search_players("Shohei Ohtani")

if players:
    display_player_card_streamlit(players[0])
```

#### `is_image_accessible(url, timeout=3)`

Check if an image URL is accessible.

**Parameters:**
- `url` (str): Image URL to check
- `timeout` (int): Request timeout in seconds

**Returns:** True if accessible, False otherwise

## 🔧 How It Was Implemented

### Files Modified/Created

1. **`src/player_images.py` (NEW)**
   - URL generation functions for headshots, action shots, team logos
   - Streamlit display function
   - Image accessibility checker

2. **`streamlit_app.py` (MODIFIED)**
   - Added import: `from player_images import get_player_headshot_url`
   - Added `display_player_card()` function
   - Integrated player card display for:
     * Career breakdown queries
     * Single player stat queries
     * Player ranking queries

### Technical Details

**MLB CDN Structure:**
- Hosted on Cloudinary (cloud image service)
- Predictable URL pattern based on player ID
- Automatic quality optimization (`q_auto:best`)
- Default fallback image if player photo missing
- Cached by CDN for fast loading

**Player ID Lookup:**
- Uses existing `MLBDataFetcher.search_players()` method
- Returns player ID from MLB Stats API
- Player ID is stable (doesn't change)

## 🎯 Example Queries

Try these queries to see player cards:

```
"Show me Aaron Judge's career stats"
"What was Shohei Ohtani's batting average in 2024?"
"Gunnar Henderson career home runs"
"Where does Adley Rutschman rank in hits?"
"Corbin Burnes ERA in 2024"
```

## 📝 Notes

### About Player Images

- **Always Current**: MLB updates these images automatically
- **No Copyright Issues**: These are official MLB images for legitimate use
- **Generic Fallback**: If a player's photo isn't available, a generic baseball silhouette appears
- **Fast Loading**: Images are CDN-cached and optimized

### Topps Baseball Cards

**Question:** "Does Topps provide an API for baseball card images?"

**Answer:** No, Topps does not provide a public API for their baseball card images. Their card images are copyrighted collectibles. 

However, we use MLB's official player headshots instead, which are:
- Publicly available
- Free to use
- Always current
- Professional quality
- Automatically updated

This provides the "baseball card" experience using official MLB player photos!

### Alternative Image Sources

If you need additional baseball images:

1. **MLB.com Official Images**
   - Headshots (used in this app) ✅
   - Action shots ✅
   - Team logos ✅
   - FREE

2. **Sportradar Images & Editorial API**
   - Player headshots
   - Action shots
   - Coach and venue images
   - Editorial articles
   - **Paid service** (B2B only)
   - Requires commercial account

3. **ESPN/Sports Media**
   - Various player images
   - **Copyright restrictions**
   - Not suitable for apps

## 🚀 Future Enhancements

Possible additions:

1. **Team Logos**
   - Display team logo alongside team queries
   - Already implemented: `get_team_logo_url()`

2. **Action Shots**
   - Show dynamic player photos for exciting moments
   - Already implemented: `get_player_action_shot_url()`

3. **Historical Players**
   - Vintage photos for retired players
   - May require additional research

4. **Custom Card Styling**
   - Border designs
   - Team color theming
   - Stats overlay on image

## 🆘 Troubleshooting

### Image Not Displaying

**Problem:** Player card shows broken image icon

**Possible Causes:**
1. Player ID not found (check spelling)
2. Network connectivity issue
3. MLB CDN temporarily unavailable

**Solutions:**
```python
# Test image accessibility
from src.player_images import is_image_accessible, get_player_headshot_url

url = get_player_headshot_url(592450)  # Aaron Judge
if is_image_accessible(url):
    print("✓ Image available!")
else:
    print("✗ Image not accessible")
```

### Generic Placeholder Showing

**Problem:** Seeing silhouette instead of player photo

**Cause:** MLB doesn't have a current photo for this player

**Notes:**
- Common for newly called-up players
- May occur for recently retired players
- Generic image is intentional fallback

### Player Not Found

**Problem:** "Could not find player" message

**Solutions:**
1. Check spelling of player name
2. Try full name instead of nickname
3. Verify player is in MLB system
4. For retired players, check if they played recently enough

## 📚 References

- **MLB Stats API**: https://statsapi.mlb.com/
- **MLB Player Images**: https://img.mlbstatic.com/
- **Cloudinary Documentation**: https://cloudinary.com/documentation
- **MLB.com**: https://www.mlb.com/

## 💡 Tips

1. **Fast Loading**: Images are CDN-cached - first load may be slow, subsequent loads instant
2. **Offline Cache**: Browser caches images automatically
3. **High Quality**: Use 'large' size for printing or detailed views
4. **Accessibility**: Always include alt text for screen readers
5. **Fallback**: Code handles missing images gracefully with placeholders

---

**Feature Added:** November 30, 2025  
**Version:** 1.1.0+  
**Dependencies:** None (uses standard libraries + requests)  
**Status:** ✅ Production Ready
