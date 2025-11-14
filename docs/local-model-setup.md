# Local Model Setup Guide

## Migration from OpenAI to Hugging Face Transformers

This project has been migrated from OpenAI's API to local Hugging Face models for reduced latency and offline capability.

## Benefits

- **Lower Latency**: No network calls, instant local inference
- **Cost Savings**: No API fees
- **Privacy**: All processing happens locally
- **Offline Capability**: Works without internet connection (after initial model download)

## Installation

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- `torch` - PyTorch for running models
- `transformers` - Hugging Face library
- `accelerate` - For optimized loading and inference

### 2. First Run (Model Download)

On first run, the model will be automatically downloaded from Hugging Face Hub (~3.5GB for SmolLM2):

```powershell
python -m src
```

The model will be cached in your home directory (`~/.cache/huggingface/`) and reused for subsequent runs.

## Default Model

**HuggingFaceTB/SmolLM2-1.7B-Instruct** (1.7B parameters)
- Very fast inference on CPU and GPU
- Good instruction following for narration tasks
- Optimized for low latency
- Small download size (~3.5GB)

## Alternative Models

You can change the model in `narrator.py` by modifying the default parameter:

### Ultra-Fast Options (1-2B parameters)
```python
# Qwen 1.5B - extremely fast
NarratorAgent(model="Qwen/Qwen2.5-1.5B-Instruct")

# SmolLM 1.7B - very fast, good quality
NarratorAgent(model="HuggingFaceTB/SmolLM2-1.7B-Instruct")
```

### Balanced Options (3-4B parameters)
```python
# Phi-3 (higher quality than default)
NarratorAgent(model="microsoft/Phi-3-mini-4k-instruct")

# Phi-3.5
NarratorAgent(model="microsoft/Phi-3.5-mini-instruct")
```

### Higher Quality Options (7B+ parameters)
```python
# Mistral 7B - slower but higher quality
NarratorAgent(model="mistralai/Mistral-7B-Instruct-v0.3")

# Llama 3.2 8B
NarratorAgent(model="meta-llama/Llama-3.2-8B-Instruct")
```

## Performance

### Expected Latency (CPU - AMD Ryzen 5000 series or Intel 11th gen+)
- **SmolLM 1.7B (default)**: ~1-2 seconds per narration
- **Qwen 1.5B**: ~1-2 seconds per narration
- **Phi-3.5 (3.8B)**: ~2-5 seconds per narration

### Expected Latency (GPU - NVIDIA RTX 3060 or better)
- **All 1-2B models**: <0.2 seconds per narration
- **Phi-3.5 (3.8B)**: ~0.2-0.5 seconds per narration
- **Mistral 7B**: ~0.5-1 second per narration

## GPU Acceleration

If you have an NVIDIA GPU with CUDA support:

1. Install CUDA-enabled PyTorch:
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

2. The narrator will automatically detect and use your GPU

## Troubleshooting

### Out of Memory Errors

If you get OOM errors:

1. **Use a smaller model**: Switch to Qwen 1.5B or SmolLM 1.7B
2. **Reduce max_new_tokens**: In narrator.py, change `max_new_tokens=80` to `max_new_tokens=50`
3. **Use CPU**: The code will automatically fall back to CPU if GPU memory is insufficient

### Slow First Run

The first time you run the server, it needs to download the model (~3.5GB for SmolLM2, ~7-8GB for Phi-3). This is a one-time operation.

### Import Errors

Make sure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

## Code Changes Summary

### Before (OpenAI)
```python
import openai
client = openai.OpenAI(api_key=api_key)
response = client.chat.completions.create(model="gpt-4", messages=[...])
```

### After (Local Model)
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
outputs = model.generate(**inputs)
```

## Environment Variables

You no longer need `OPENAI_API_KEY` in your `.env` file. You can remove it.

## Testing

Run the example script to verify setup:
```powershell
python src/example.py
```

This will generate a test response using the local model.
