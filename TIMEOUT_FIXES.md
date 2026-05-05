# HTTP Timeout Fixes - Cold Email Engine

## 🔧 Changes Made

### 1. **Increased Timeouts**
   - Connection check: **5s → 15s**
   - LLM generation: **30s → 120s (2 minutes)**
   - Reason: LLaMA 3 model takes time to load and generate responses

### 2. **Added Connection Retry Logic**
   - Automatic retry with exponential backoff
   - Handles transient network failures
   - Retries on status codes: 429, 500, 502, 503, 504

### 3. **HTTP Connection Pooling**
   - Reuses connections via `HTTPAdapter`
   - Reduces overhead for multiple requests
   - Session-based connections instead of per-request

### 4. **Better Error Handling**
   - Distinguishes between timeout, connection error, and other errors
   - Provides helpful troubleshooting tips
   - Graceful fallback to mock generation

## 🚀 How to Use

### Option 1: Normal Run (Uses Ollama if available)
```bash
python run_demo.py
```
Then open http://localhost:8000

### Option 2: Demo Mode (Mock generation, no timeout risk)
If Ollama isn't running, the system automatically uses mock responses.

## ⚡ Troubleshooting

### Error: "Ollama connection timeout (15s exceeded)"
**Solution:**
```bash
# Make sure Ollama is running in another terminal
ollama serve

# Or pull the model first
ollama pull llama3
```

### Error: "Cannot connect to Ollama at http://localhost:11434"
**Solutions:**
1. Check if Ollama is installed: `ollama --version`
2. Ensure Ollama is running on port 11434
3. On Windows, run: `ollama serve`

### Error: "Timeout after 120s - model is taking too long"
**Solutions:**
1. Your system might be slow. Try a smaller model:
   ```bash
   ollama pull mistral
   ```
   Then in `services/llm_service.py`, change:
   ```python
   self.model_name = "mistral:latest"  # Faster than llama3
   ```

2. Check available RAM - LLaMA 3 needs 8GB+
3. Close other applications to free up RAM

### Everything works now? ✅
Great! The timeouts should be fixed. The system will:
- Wait up to 15 seconds for Ollama connection
- Wait up to 2 minutes for message generation
- Retry on transient failures
- Fall back to mock generation if Ollama unavailable

## 📊 Performance Tips

1. **First generation is slower** - Model needs to load into RAM
2. **Subsequent generations are faster** - Model stays in memory
3. **Use smaller model for faster responses** - `mistral` ~7s, `llama3` ~15-30s
4. **Increase RAM** - More RAM = faster generation

## 🔍 Debug Output

When running, you'll see:
```
🔍 Checking Ollama connection...
✅ Connected to Ollama with llama3:latest
🤖 [OLLAMA] Generating with LLaMA 3... (max 500 tokens)
✅ [OLLAMA] Generated XXX chars in 24.5s
```

If it falls back to mock:
```
🔄 Using fallback generation (Ollama not available)
⚠️  Using FALLBACK generation (not Ollama)
```

## 📝 Key Changes in Code

**Before:**
```python
timeout=5  # Too short
requests.post(...)  # No retry logic
```

**After:**
```python
timeout=120  # Sufficient for LLaMA 3
self.session.post(...)  # With retries and pooling
```
