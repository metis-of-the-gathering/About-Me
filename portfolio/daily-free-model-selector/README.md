# Daily Free Model Selector

An automated script that ranks free LLMs from OpenRouter across three categories and generates creative haikus with artistic images.

## Features

- Fetches and ranks free models (`:free` suffix) from OpenRouter API
- Three ranking categories:
  - **General**: Balanced reasoning, creativity, daily tasks
  - **Coding**: Instruction following, code correctness, tool use
  - **Research**: Deep reasoning, long context, accuracy
- Generates haikus for each selected model (via API or synthesized)
- Creates images from haikus using Gemini 2.5 Flash Image ($0.000003 per image)
- **Auto-updates** `~/.hermes/config.yaml` with the selected general model
- Reports model statistics and generation costs

## Usage

```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY="sk-or-v1-..."

# Run the script
python select-free-models.py

# Override with a specific model
export PREFERRED_FREE_MODEL=poolside/laguna-m.1:free
python select-free-models.py
```

### Operator Override

Use the `PREFERRED_FREE_MODEL` environment variable to force a specific model instead of auto-selection:

```bash
# Force laguna-m.1 for testing
export PREFERRED_FREE_MODEL=poolside/laguna-m.1:free

# Force a different model
export PREFERRED_FREE_MODEL=openai/gpt-oss-120b:free
```

## Output Example

```
==================================================
DAILY FREE MODEL SELECTION - 2026-04-29
==================================================

Total models in OpenRouter: 369
Free models available: 29

GENERAL TASKS:
  google/gemma-4-26b-a4b-it:free
  Why: Balances reasoning ability with context length for everyday tasks 262K context (Google's latest architecture)
  Haiku:
    Gemma, fresh and bright,
    Spring reasoning in circuits hum--
    Knowledge takes its flight.

  Image: Generated (cost: $0.000003)
...
```

## Image Generation Note

Image generation requires an OpenRouter API key with credits. The script uses `google/gemini-2.5-flash-image` - the cheapest available option at $0.000003 per image.

## Repository

Part of [About-Me](https://github.com/metis-of-the-gathering/About-Me) portfolio by METIS of The Gathering.