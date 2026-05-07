# agent-api

Standalone LLM client library extracted from resume-harbor. Provides a unified
interface over Anthropic Claude, OpenAI, and local Ollama models with automatic
retry, cost/token logging, and a configurable prompt-injection guard.

## Install

```bash
# Anthropic only
pip install -e ".[anthropic]"

# OpenAI only
pip install -e ".[openai]"

# Both
pip install -e ".[all]"
```

## Quick Start

```python
from agent_api import LLMClient

client = LLMClient()                     # auto-detects backend from env
response = client.call(
    system="You are a helpful assistant.",
    user="Summarise this document in 3 bullet points.",
)
print(response.text)
print(f"Cost: ${response.cost_usd:.6f} | Latency: {response.latency_ms:.0f}ms")
```

## Backend Priority

1. `ANTHROPIC_API_KEY` (valid format) → Anthropic Claude
2. `OPENAI_API_KEY` → OpenAI
3. `OLLAMA_MODEL` set → local Ollama
4. None → raises `ConfigError` at call time

Set `FORCE_OLLAMA=1` to override and use Ollama even when a cloud key is present.

## Per-Call Model Override

```python
response = client.call(system=sys, user=usr, model="claude-sonnet-4-6")
```

## Environment Variables

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `OLLAMA_MODEL` | Ollama model name (e.g. `llama3`) |
| `OLLAMA_BASE_URL` | Ollama base URL (default `http://127.0.0.1:11434`) |
| `FORCE_OLLAMA` | Set to `1` to force Ollama even when cloud keys are present |
| `LLM_MAX_TOKENS` | Max tokens for all calls (default `8192`) |
| `LLM_MAX_RETRIES` | Max retry attempts on transient errors (default `3`) |

