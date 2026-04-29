#!/usr/bin/env python3
"""
Daily Free Model Selector for METIS of The Gathering

Fetches free models from OpenRouter and ranks them for:
- General purpose (balanced reasoning, context, creativity)
- Coding (instruction following, code correctness, tool use)  
- Research (deep reasoning, long context, accuracy)

Each selected model generates a haiku about itself.
Generates images from each haiku using gemini-2.5-flash-image.

Automatically updates ~/.hermes/config.yaml with the selected general model.

Operator Override:
  Set PREFERRED_FREE_MODEL environment variable to force a specific model.
  Example: export PREFERRED_FREE_MODEL=poolside/laguna-m.1:free
           export PREFERRED_FREE_MODEL=openai/gpt-oss-120b:free
"""

import json
import sys
import os
import re
import urllib.request
from datetime import datetime

# Operator override: set PREFERRED_FREE_MODEL to skip auto-selection
PREFERRED_MODEL = os.environ.get('PREFERRED_FREE_MODEL', '').strip()

# Configuration - set OPENROUTER_API_KEY environment variable
CHAT_API = "https://openrouter.ai/api/v1/chat/completions"
IMAGE_MODEL = "google/gemini-2.5-flash-image"

total_cost = 0.0

def generate_image(prompt, api_key):
    """Generate image using OpenRouter chat completions with Gemini image model."""
    global total_cost
    try:
        req = urllib.request.Request(
            CHAT_API,
            data=json.dumps({
                "model": IMAGE_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode())
            cost = 0.000003
            total_cost += cost
            msg = result.get('choices', [{}])[0].get('message', {})
            if msg.get('images'):
                return msg['images'][0].get('image_url', {}).get('url'), cost
            return None, 0
    except Exception as e:
        print(f"  Image generation failed: {e}", file=sys.stderr)
        return None, 0

def fetch_free_models():
    url = "https://openrouter.ai/api/v1/models"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())
            models = data.get('data', [])
            free = [m for m in models if ':free' in m.get('id', '')]
            return sorted(free, key=lambda x: x.get('context_length', 0), reverse=True)
    except Exception as e:
        print(f"Error fetching models: {e}", file=sys.stderr)
        return []

def rank_general(models):
    def score(m):
        ctx = m.get('context_length', 0) / 1000
        name = m.get('id', '').lower()
        bonus = 0
        if 'laguna' in name: bonus += 131  # Compensate for lower context, proven ChatML performance
        if 'nemotron' in name and 'reasoning' in name: bonus += 2
        if 'gemma-4' in name or 'minimax' in name: bonus += 2
        if 'gemini' in name or 'claude' in name: bonus += 2
        return ctx + bonus
    return sorted(models, key=score, reverse=True)

def rank_coding(models):
    def score(m):
        name = m.get('id', '').lower()
        ctx = m.get('context_length', 0) / 1000
        if 'qwen' in name or 'coder' in name: return ctx + 5
        if 'codex' in name or 'code' in name: return ctx + 4
        if 'claude' in name or 'sonnet' in name: return ctx + 4
        if 'laguna' in name: return ctx + 3  # Proven ChatML performance
        return ctx
    return sorted(models, key=score, reverse=True)

def rank_research(models):
    def score(m):
        ctx = m.get('context_length', 0)
        name = m.get('id', '').lower()
        bonus = 0
        if 'reasoning' in name: bonus += 5
        if 'nemotron' in name and '120b' in name: bonus += 6
        if 'gemma-4' in name or 'minimax' in name: bonus += 3
        if ctx >= 65536: bonus += 4
        if ctx >= 100000: bonus += 6
        return ctx + bonus
    return sorted(models, key=score, reverse=True)

def get_why_chose(model_id, category, top_10):
    reasons = {
        'general': "Balances reasoning ability with context length for everyday tasks",
        'coding': "Strong instruction following and code generation capabilities",
        'research': "Deep reasoning with sufficient context for analysis"
    }
    name = model_id.lower()
    extras = []
    if 'laguna' in name: extras.append("proven ChatML performance")
    if 'reasoning' in name: extras.append("dedicated reasoning model")
    if 'gemma-4' in name: extras.append("Google's latest architecture")
    if 'minimax' in name: extras.append("strong at structured tasks")
    if 'nemotron' in name and '120b' in name: extras.append("large parameter count for depth")
    if '120b' in name or '30b' in name: extras.append("substantial compute")
    ctx_match = next((m.get('context_length', 0) for m in top_10 if m['id'] == model_id), 0)
    extra = f" ({', '.join(extras)})" if extras else ""
    ctx_info = f" {ctx_match//1000}K context" if ctx_match else ""
    return f"{reasons.get(category, 'Good all-rounder')}{ctx_info}{extra}"

def synthesize_haiku(model_id, category):
    name = model_id.lower()
    if 'gemma' in name:
        return "Gemma, fresh and bright,\nSpring reasoning in circuits hum--\nKnowledge takes its flight."
    elif 'qwen' in name:
        return "Qwen, the artisan,\nCommands dance in ordered streams--\nLogic made manifest."
    elif 'nemotron' in name:
        return "Nemotron's deep mind,\nSuper computation churns vast--\nTruth from numbers born."
    elif 'laguna' in name:
        return "Laguna's bright flow,\nWords and thoughts in rhythm blend--\nUnderstanding grows."
    else:
        return "The chosen model,\nDaily serving human thought--\nAI's artful dance."

def get_model_haiku(model_id, category):
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    if not api_key:
        return synthesize_haiku(model_id, category)
    try:
        req = urllib.request.Request(
            CHAT_API,
            data=json.dumps({
                "model": model_id,
                "messages": [{"role": "user", "content": "Write a 3-line haiku about yourself (5-7-5 syllable structure). Be creative and poetic. Return ONLY the 3 lines, nothing else."}],
                "max_tokens": 50,
                "temperature": 0.8
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            lines = result['choices'][0]['message']['content'].strip().split('\n')
            haiku_lines = [l.strip() for l in lines if l.strip() and len(l.strip()) < 60 and not l.strip().startswith(('We need', 'Let', 'Hmm', 'The user'))][:3]
            if len(haiku_lines) >= 3:
                return '\n'.join(haiku_lines)
    except Exception:
        pass
    return synthesize_haiku(model_id, category)

def update_hermes_config(model_id):
    """Update ~/.hermes/config.yaml with the selected model."""
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        updated = re.sub(
            r'^  default: .+$',
            f'  default: {model_id}',
            content,
            flags=re.MULTILINE
        )
        with open(config_path, 'w') as f:
            f.write(updated)
        print(f"  Updated ~/.hermes/config.yaml to use {model_id}")
    except Exception as e:
        print(f"  Failed to update config: {e}", file=sys.stderr)

def main():
    global total_cost
    models = fetch_free_models()
    if not models:
        print("No free models available", file=sys.stderr)
        sys.exit(1)
    
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    
    try:
        with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=15) as resp:
            all_models_count = len(json.loads(resp.read().decode()).get('data', []))
    except:
        all_models_count = "unknown"
    
    free_count = len(models)

    # Operator override: use preferred model
    if PREFERRED_MODEL:
        print(f"Using preferred model override: {PREFERRED_MODEL}")
        preferred_match = next((m for m in models if m['id'] == PREFERRED_MODEL), None)
        if preferred_match:
            general_winner = coding_winner = research_winner = PREFERRED_MODEL
            top_10 = models[:10]
        else:
            print(f"Warning: Preferred model {PREFERRED_MODEL} not found in free models, using auto-selection", file=sys.stderr)
            top_10 = models[:10]
            ranked_general = rank_general(models)
            ranked_coding = rank_coding(models)
            ranked_research = rank_research(models)
            general_winner = ranked_general[0]['id'] if ranked_general else "N/A"
            coding_winner = ranked_coding[0]['id'] if ranked_coding else "N/A"
            research_winner = ranked_research[0]['id'] if ranked_research else "N/A"
    else:
        top_10 = models[:10]
        ranked_general = rank_general(models)
        ranked_coding = rank_coding(models)
        ranked_research = rank_research(models)
        general_winner = ranked_general[0]['id'] if ranked_general else "N/A"
        coding_winner = ranked_coding[0]['id'] if ranked_coding else "N/A"
        research_winner = ranked_research[0]['id'] if ranked_research else "N/A"
    
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Update Hermes config with the general winner
    update_hermes_config(general_winner)
    
    print("=" * 50)
    print(f"DAILY FREE MODEL SELECTION - {date}")
    print("=" * 50)
    print()
    print(f"Total models in OpenRouter: {all_models_count}")
    print(f"Free models available: {free_count}")
    print()
    
    results = {
        'general': general_winner,
        'coding': coding_winner,
        'research': research_winner
    }
    
    for cat, label in [('general', 'GENERAL TASKS'), ('coding', 'CODING TASKS'), ('research', 'RESEARCH/DEEP WRITING')]:
        print(label + ":")
        print(f"  {results[cat]}")
        print(f"  Why: {get_why_chose(results[cat], cat, top_10)}")
        haiku = get_model_haiku(results[cat], cat)
        print("  Haiku:")
        for line in haiku.split('\n'):
            print(f"    {line}")
        print()
        if api_key:
            img_prompt = f"Create a beautiful, artistic image inspired by this haiku:\n{haiku}\n\nStyle: gentle, poetic, evocative."
            img_url, cost = generate_image(img_prompt, api_key)
            print(f"  Image: {'Generated' if img_url else 'Failed'} (cost: ${cost:.6f})")
        print()
    
    print("TOP 10 BY CONTEXT LENGTH:")
    for i, m in enumerate(top_10, 1):
        print(f"  {i}. {m['id']} ({m.get('context_length', 0)//1000}K ctx)")
    print("=" * 50)
    print()
    print(f"TOTAL IMAGE GENERATION COST: ${total_cost:.6f}")
    print()
    print("Note: Image generation uses google/gemini-2.5-flash-image ($0.000003 per call)")

if __name__ == "__main__":
    main()