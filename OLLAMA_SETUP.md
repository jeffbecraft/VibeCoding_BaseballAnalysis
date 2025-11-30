# Using Free AI Models with Ollama

## Overview
Ollama lets you run powerful AI models completely FREE on your local computer. No API keys, no costs, no internet required (after initial download).

## Quick Setup

### 1. Install Ollama
Download from: https://ollama.com/download

### 2. Download a Model
Open PowerShell and run:
```powershell
# Recommended: Fast, good quality (4GB)
ollama pull llama3.2

# Alternative: Smaller, faster (2GB)
ollama pull phi3

# Alternative: Larger, better quality (7GB)
ollama pull mistral
```

### 3. Install Python Package
```powershell
.\.venv\Scripts\Activate.ps1
pip install ollama
```

### 4. Run Your App
No API key needed! The AI query handler will automatically detect and use Ollama.

## Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2** | 4GB | Fast | Good | General use (recommended) |
| phi3 | 2GB | Very Fast | Decent | Quick responses |
| mistral | 7GB | Medium | Excellent | Complex queries |
| codellama | 7GB | Medium | Excellent | Code generation |

## Configuration

Set your preferred model in environment variable:
```powershell
$env:OLLAMA_MODEL = "llama3.2"
```

Or edit `src/ai_query_handler.py` and change the default model.

## Advantages Over OpenAI

✅ **Completely Free** - No API costs ever  
✅ **Private** - All processing happens locally  
✅ **Fast** - No internet latency  
✅ **Offline** - Works without internet  
✅ **No Rate Limits** - Use as much as you want  

## Disadvantages

❌ Requires ~4-8GB disk space  
❌ Slower than cloud GPT-4 (2-5 seconds vs 1-2 seconds)  
❌ Slightly lower quality than GPT-4  
❌ Requires decent CPU/RAM  

## Performance Tips

1. **First query is slow** (model loads into memory) - subsequent queries are fast
2. **Keep Ollama running** in background for better performance
3. **Use smaller models** (phi3) if you have limited RAM
4. **Use larger models** (mistral, codellama) for complex queries

## Troubleshooting

**"Ollama not found"**
- Install from https://ollama.com/download
- Restart terminal after installation

**"Model not found"**
- Run: `ollama pull llama3.2`
- Wait for download to complete

**Slow responses**
- First query loads model (10-30 seconds)
- Subsequent queries are faster (2-5 seconds)
- Consider using smaller model (phi3)

**Out of memory**
- Close other applications
- Use smaller model (phi3 instead of llama3.2)
- Restart Ollama: `ollama serve`

## Hybrid Approach

You can use **both** Ollama and OpenAI:
- Ollama for development/testing (free)
- OpenAI for production (better quality)

The AI handler automatically chooses based on what's available.
