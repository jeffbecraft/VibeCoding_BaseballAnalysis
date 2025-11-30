# Free AI Setup with Ollama

## Why Ollama?

✅ **Completely FREE** - No API costs, ever  
✅ **Private** - All processing on your computer  
✅ **No API Keys** - No sign-ups or registration  
✅ **Offline** - Works without internet (after model download)  
✅ **Fast** - No network latency  

## Quick Setup (5 minutes)

### 1. Install Ollama

**Windows:**
- Download from: https://ollama.com/download
- Run the installer
- Ollama will start automatically

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Download a Model

Open PowerShell/Terminal and run:

```powershell
# Recommended: Good balance of speed and quality (4GB download)
ollama pull llama3.2

# Alternative: Faster, smaller (2GB download)
ollama pull phi3

# Alternative: Better quality, slower (7GB download)
ollama pull mistral
```

### 3. Install Python Package

In your project directory:

```powershell
.\.venv\Scripts\Activate.ps1
pip install ollama
```

### 4. Run Your App

```powershell
streamlit run streamlit_app.py
```

That's it! The app will automatically detect and use Ollama.

## Choosing a Model

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2** | 4GB | Fast | Good | Recommended for most users |
| phi3 | 2GB | Very Fast | Decent | Limited RAM or quick testing |
| mistral | 7GB | Medium | Excellent | Complex queries, more RAM |
| codellama | 7GB | Medium | Excellent | Code-heavy queries |

## Switching Models

To use a different model:

```powershell
# Download the model
ollama pull mistral

# Set environment variable (optional)
$env:OLLAMA_MODEL = "mistral"

# Or edit src/ai_query_handler.py and change default
```

## Performance Notes

- **First query:** 10-30 seconds (model loads into RAM)
- **Subsequent queries:** 2-5 seconds (model already loaded)
- **Keep Ollama running** for best performance
- **Close other apps** if low on RAM

## Troubleshooting

### "Ollama not found"
- Install from https://ollama.com/download
- Restart your terminal/PowerShell
- Check if running: `ollama list`

### "Model not found"
- Download model: `ollama pull llama3.2`
- Wait for download to complete
- Verify: `ollama list` (should show your models)

### Slow responses
- First query is always slower (loading model)
- Close memory-intensive apps
- Try smaller model: `ollama pull phi3`

### Out of memory
- Close other applications
- Use smaller model (phi3 instead of llama3.2)
- Restart Ollama: 
  ```powershell
  # Windows: Restart Ollama from system tray
  # Mac/Linux: 
  killall ollama
  ollama serve
  ```

## Comparison: Ollama vs OpenAI

| Feature | Ollama | OpenAI |
|---------|--------|--------|
| **Cost** | FREE | $0.01-$0.05/query |
| **Setup** | 5 minutes | Get API key |
| **Privacy** | Complete | Data sent to cloud |
| **Speed** | 2-5 sec | 1-2 sec |
| **Quality** | Very Good | Excellent |
| **Internet** | Not needed | Required |
| **Limits** | None | Rate limits apply |

## Using Both

You can have both installed! The app will:
1. Try Ollama first (free)
2. Fallback to OpenAI if Ollama unavailable

This lets you:
- Use Ollama for development (free)
- Use OpenAI for production (better quality)

## Model Management

```powershell
# List installed models
ollama list

# Remove a model
ollama rm llama3.2

# Update a model
ollama pull llama3.2

# See running models
ollama ps
```

## Advanced Configuration

Set model in code (`src/ai_query_handler.py`):

```python
# Change default model
def _init_ollama(self) -> bool:
    # ...
    self.model = "mistral"  # or phi3, codellama, etc.
```

Or set environment variable:

```powershell
$env:OLLAMA_MODEL = "mistral"
```

## Getting Help

- Ollama docs: https://ollama.com/docs
- Model library: https://ollama.com/library
- This project's AI guide: `AI_QUERY_GUIDE.md`
