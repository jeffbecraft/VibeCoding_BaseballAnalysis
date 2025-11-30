# Retry Feature Documentation

## Overview
The retry feature allows users to regenerate AI answers if they're unsatisfied with the initial response. This is especially useful when the AI generates incorrect code or takes an unexpected approach.

## How to Use

### For AI-Generated Answers
1. After receiving an AI-generated answer, scroll to the bottom
2. Look for the section: **"Not satisfied with this answer?"**
3. Click the **"🔄 Retry with Fresh AI"** button
4. The cached answer will be cleared and a fresh response generated
5. The page will automatically refresh with the new answer

### For Error Messages
1. If a query fails with an error, look for the retry options at the bottom
2. Click **"🔄 Retry Question"** to clear cache and try again
3. Or click **"📝 Edit Query"** for guidance on rephrasing

## What Happens When You Retry

1. **Cache Cleared**: The specific cached AI code for your query is removed
2. **Fresh Generation**: AI generates completely new code (not from cache)
3. **New Approach**: May use different logic or methods to answer
4. **Automatic Execution**: New code runs immediately after generation

## When to Use Retry

✅ **Good use cases:**
- AI gave wrong answer (e.g., said Henderson had more when Judge did)
- Generated code had errors
- Answer was incomplete or unclear
- Want to see if a different approach works better

❌ **Not needed when:**
- Answer is correct (no benefit from retry)
- Question was ambiguous (better to rephrase instead)
- Looking for slightly different data (modify query instead)

## Technical Details

### Cache Management
- Each query creates a unique cache key based on:
  - Normalized question text
  - Season/year mentioned in query
  - MD5 hash for filename

- Retry removes only that specific cache entry
- Other cached queries remain unaffected

### Code Generation
- First attempt: Uses cache if available (~0.01s)
- After retry: Generates fresh code (2-5s)
- Fresh code is cached again for future use

### User Feedback
- **"✓ Cached answer cleared!"** - Cache was found and removed
- **"Generating new response..."** - No cache existed (already fresh)
- Automatic page refresh shows new result

## Example Usage

### Scenario: Comparison Query Issue
```
User asks: "Who had more doubles in 2024, Henderson or Judge?"

First attempt:
- AI generates code comparing players
- Returns: "Henderson had 31 doubles"
- Missing Judge's data (incorrect)

User clicks "🔄 Retry with Fresh AI":
- Cache cleared
- New AI code generation
- Returns: "Judge had more doubles (36 vs 31)" ✓ Correct!
```

### Scenario: Error Recovery
```
User asks: "Top 5 ERA leaders 2024"

First attempt:
- AI generates code with syntax error
- Error: "Unauthorized import: MLB"

User clicks "🔄 Retry Question":
- Cache cleared
- New code generated
- Success: Shows top 5 pitchers ✓
```

## Implementation Notes

### For Developers

**AICodeCache.remove()**
```python
def remove(self, cache_key: str) -> bool:
    """Remove specific cached query by key."""
    cache_file = os.path.join(self.cache_dir, f"{cache_key}.code")
    if os.path.exists(cache_file):
        os.remove(cache_file)
        return True
    return False
```

**Streamlit Integration**
```python
if st.button("🔄 Retry with Fresh AI"):
    cache = AICodeCache()
    cache_key = cache._generate_cache_key(query, season)
    removed = cache.remove(cache_key)
    st.rerun()  # Refresh page to execute query again
```

### Testing
Run `python test_retry_feature.py` to verify:
- ✓ Cache removal works correctly
- ✓ Fresh code generation after retry
- ✓ Cache is repopulated with new code
- ✓ Retry doesn't affect other cached queries

## Future Enhancements

Possible improvements:
1. **Retry with feedback**: Let user specify what was wrong
2. **Compare attempts**: Show both old and new answers
3. **Retry count**: Limit retries to prevent infinite loops
4. **Retry all**: Clear entire cache at once
5. **Auto-retry**: Retry automatically on certain error types
