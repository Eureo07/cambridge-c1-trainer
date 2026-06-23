"""
ai_client.py — Wrapper for OpenRouter API calls (free tier).
Set your API key in environment variable OPENROUTER_API_KEY.
"""

import os
import json
import urllib.request
import urllib.error

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "liquid/lfm-2.5-1.2b-instruct:free"


def call(prompt: str, system: str = None, max_tokens: int = 1000) -> str:
    """Make a call to OpenRouter API (free Mistral 7B). Returns text response."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return "[ERROR] OPENROUTER_API_KEY not set."

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return f"[API ERROR {e.code}] {body}"
    except Exception as e:
        return f"[ERROR] {str(e)}"
