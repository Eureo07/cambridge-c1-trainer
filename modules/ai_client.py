"""
ai_client.py — Wrapper for Anthropic Claude API calls.
Set your API key in environment variable ANTHROPIC_API_KEY.
"""

import os
import json
import urllib.request
import urllib.error

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

def call(prompt: str, system: str = None, max_tokens: int = 1000) -> str:
    """Make a single call to Claude API. Returns text response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "[ERROR] ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY=your_key"

    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }
    if system:
        payload["system"] = system

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    try:
        req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["content"][0]["text"]
    except urllib.error.HTTPError as e:
        return f"[API ERROR {e.code}] {e.read().decode()}"
    except Exception as e:
        return f"[ERROR] {str(e)}"
