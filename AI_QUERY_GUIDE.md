# 🤖 AI-Powered Query System

## Overview

The MLB Statistics application now includes an **AI-powered fallback system** that can answer virtually any baseball statistics question, even if it doesn't match a predefined query pattern.

## How It Works

### Standard Flow (Fast)
```
User Question → Pattern Matching → MLB API → Results
```

### AI-Powered Fallback (Flexible)
```
User Question → Pattern Matching FAILS → AI Generates Code → Validates → Executes → Results
```

### Architecture

1. **User asks a question** in natural language
2. **Standard parser tries** to match predefined patterns
3. **If standard parser fails:**
   - AI receives the question
   - AI generates Python code using MLB API
   - Code is validated for safety
   - Code executes in sandboxed environment
   - Results returned to user

## Setup

### 1. Install OpenAI Package

```bash
pip install openai
```

### 2. Get OpenAI API Key

1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy the key (starts with `sk-...`)

### 3. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"

# Or permanently:
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')
```

**macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-your-key-here"

# Or add to ~/.bashrc or ~/.zshrc:
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.bashrc
```

### 4. Run the Application

```bash
streamlit run streamlit_app.py
```

## Example Queries

### Standard Queries (Fast - No AI Needed)
These work with predefined patterns:
- "Top 10 home runs in 2024"
- "What was Shohei Ohtani's batting average in 2024?"
- "Rank Aaron Judge's home runs"
- "ERA leaders for the Yankees"

### AI-Powered Queries (Flexible)
These work with AI code generation:
- "Who had the most stolen bases on the Dodgers in 2024?"
- "Compare Shohei Ohtani and Aaron Judge batting average"
- "What percentage of pitches thrown by Gerrit Cole were strikes in 2024?"
- "Show me all players with over 30 home runs and 100 RBIs"
- "Which rookie had the best OPS in the National League?"
- "Calculate the team batting average for the Red Sox"

## How AI Code Generation Works

### Step 1: AI Receives Context

The AI is given:
- Your question
- Available data fetcher methods
- Available data processor methods
- The season year

### Step 2: AI Generates Code

Example question: *"Who had the best batting average among Yankees in 2024?"*

Generated code:
```python
try:
    # Get batting average leaders
    leaders = data_fetcher.get_stats_leaders(
        'avg', 
        season, 
        100, 
        'hitting',
        team_id=147  # Yankees team ID
    )
    
    # Process the data
    processed = data_processor.extract_stats_leaders(leaders, 1)
    
    if processed:
        player = processed[0]
        result = {
            'success': True,
            'data': processed,
            'answer': f"{player['name']} had the best batting average with {player['value']:.3f}",
            'explanation': 'Retrieved hitting leaders for batting average from Yankees'
        }
    else:
        result = {'success': False, 'error': 'No data found'}
except Exception as e:
    result = {'success': False, 'error': str(e)}
```

### Step 3: Code Validation

The system checks for:
- ✅ No dangerous functions (eval, exec, os.system)
- ✅ No file operations (open, write)
- ✅ No unauthorized imports
- ✅ Valid Python syntax
- ✅ Only allowed API methods

### Step 4: Safe Execution

Code runs in a **restricted environment**:
- Only has access to `data_fetcher` and `data_processor`
- Limited built-in functions (no file I/O)
- Cannot import unauthorized modules
- Cannot access system resources

### Step 5: Results Display

- Shows the answer in natural language
- Displays data tables
- Optionally shows generated code

## Security

### What's Protected

✅ **No file system access** - Cannot read/write files  
✅ **No network access** - Cannot make external requests  
✅ **No system commands** - Cannot run shell commands  
✅ **No code injection** - eval/exec disabled  
✅ **Sandboxed execution** - Isolated environment  
✅ **Code validation** - Checks before execution  

### Blocked Patterns

- `eval()`
- `exec()`
- `__import__()`
- `open()`
- `os.system()`
- `subprocess`
- Any unauthorized imports

### Allowed Operations

- ✅ MLB API calls via data_fetcher
- ✅ Data processing via data_processor
- ✅ Pandas/NumPy operations
- ✅ Basic Python operations

## Cost Considerations

### OpenAI API Pricing

**GPT-4:**
- Input: ~$0.03 per 1000 tokens
- Output: ~$0.06 per 1000 tokens
- Average query: ~$0.01 - $0.05

**GPT-3.5-Turbo (cheaper option):**
- Input: ~$0.0005 per 1000 tokens
- Output: ~$0.0015 per 1000 tokens
- Average query: ~$0.001 - $0.005

### Cost Optimization

1. **Use standard queries when possible** - They're free and instant
2. **Consider GPT-3.5-Turbo** - 10x cheaper, still effective
3. **Set usage limits** in your OpenAI account
4. **Monitor usage** via OpenAI dashboard

To use GPT-3.5-Turbo (cheaper), edit `src/ai_query_handler.py`:
```python
self.model = "gpt-3.5-turbo"  # Instead of "gpt-4"
```

## Troubleshooting

### "AI Assistant Not Available"

**Cause:** OpenAI package not installed or API key not set

**Solution:**
```bash
pip install openai
export OPENAI_API_KEY="your-key"
```

### "API key not valid"

**Cause:** Incorrect or expired API key

**Solution:**
1. Check your key at platform.openai.com
2. Generate a new key if needed
3. Make sure you're using the right key

### "Generated code failed safety check"

**Cause:** AI tried to generate unsafe code

**Solution:**
- This is working correctly - unsafe code was blocked
- Try rephrasing your question
- Report the issue if it seems like a false positive

### "Code execution failed"

**Cause:** Generated code has a bug or data not available

**Solution:**
- Check the error message
- Try rephrasing the question more clearly
- The AI will improve with more context

### Slow responses

**Cause:** AI code generation takes 2-5 seconds

**Solution:**
- This is normal for AI queries
- Use standard queries for instant results
- Consider GPT-3.5-Turbo for faster (cheaper) responses

## Examples

### Complex Queries AI Can Handle

1. **Comparative Analysis**
   ```
   "Compare the home runs of Aaron Judge and Shohei Ohtani in 2024"
   ```

2. **Filtered Rankings**
   ```
   "Show me all Yankees players with batting average over .280"
   ```

3. **Statistical Calculations**
   ```
   "What's the average ERA of all pitchers with over 100 strikeouts?"
   ```

4. **Multi-Criteria Queries**
   ```
   "Find players with both 25+ home runs and 25+ stolen bases in 2024"
   ```

5. **Team Aggregations**
   ```
   "Calculate total RBIs for the Dodgers roster in 2024"
   ```

6. **Trend Analysis**
   ```
   "Who improved their batting average the most from 2023 to 2024?"
   ```

## Best Practices

### For Users

1. **Be specific** - "Aaron Judge home runs 2024" is better than "home runs"
2. **Include the year** - Always specify which season
3. **Use player full names** - "Shohei Ohtani" not "Ohtani"
4. **One question at a time** - Don't combine multiple unrelated queries

### For Developers

1. **Monitor AI usage** - Track costs via OpenAI dashboard
2. **Set rate limits** - Prevent abuse
3. **Cache AI results** - Store generated code for common queries
4. **Fallback gracefully** - Always have a helpful error message
5. **Log AI queries** - Track what works and what doesn't

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User Question                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   Standard Query Parser    │
        └────────────┬────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────┐            ┌─────────┐
    │ Success │            │  Failed │
    └────┬────┘            └────┬────┘
         │                      │
         │                      ▼
         │           ┌──────────────────────┐
         │           │   AI Query Handler   │
         │           └──────────┬───────────┘
         │                      │
         │                      ▼
         │           ┌──────────────────────┐
         │           │  Generate Python Code│
         │           └──────────┬───────────┘
         │                      │
         │                      ▼
         │           ┌──────────────────────┐
         │           │   Validate Safety    │
         │           └──────────┬───────────┘
         │                      │
         │                      ▼
         │           ┌──────────────────────┐
         │           │  Execute in Sandbox  │
         │           └──────────┬───────────┘
         │                      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   Display Results    │
         └──────────────────────┘
```

## Limitations

### What AI Can Do

✅ Answer any MLB statistics question  
✅ Generate complex queries  
✅ Compare multiple players/teams  
✅ Calculate aggregations  
✅ Filter and rank data  

### What AI Cannot Do

❌ Predict future outcomes  
❌ Access data not in MLB API  
❌ Modify the database  
❌ Answer non-baseball questions  
❌ Execute unsafe operations  

## Future Enhancements

Potential improvements:
1. **Caching AI-generated code** for common queries
2. **Learning from successful queries** to improve patterns
3. **Multi-turn conversations** for follow-up questions
4. **Visualization generation** - Create charts dynamically
5. **Natural language explanations** of statistics

## Support

### Getting Help

- Check the error message displayed
- View the generated code (expand "View Generated Code")
- Try rephrasing your question
- Use a standard query pattern instead

### Reporting Issues

If AI generates incorrect code:
1. Copy the generated code
2. Note the question you asked
3. Share the error message
4. Open an issue on GitHub

---

**AI-Powered Queries: Making Baseball Statistics Accessible to Everyone!** 🤖⚾

