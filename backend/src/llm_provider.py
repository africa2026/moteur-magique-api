# -*- coding: utf-8 -*-
"""
LLM Provider - Wrapper unifie multi-provider
Moteur de Rédaction Magique v5.0

Cascade: Google Gemini (gratuit) → Groq (gratuit) → OpenAI (payant) → fallback
"""

import os
import logging
import json
from typing import List, Dict, Optional

import requests as http_requests

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

_active_provider = None


def _try_gemini(messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None

    model = "gemini-2.0-flash"
    url = f"{GEMINI_API_URL}/{model}:generateContent?key={api_key}"

    system_parts = []
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            system_parts.append(msg["content"])
        elif msg["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

    body = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    if system_parts:
        body["systemInstruction"] = {"parts": [{"text": "\n".join(system_parts)}]}

    try:
        resp = http_requests.post(url, json=body, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            global _active_provider
            _active_provider = f"Gemini ({model})"
            logger.info(f"Gemini response OK ({len(text)} chars)")
            return text
        else:
            logger.warning(f"Gemini error {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        logger.warning(f"Gemini request failed: {e}")
        return None


def _try_groq(messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None

    model = "llama-3.3-70b-versatile"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        resp = http_requests.post(GROQ_API_URL, json=body, headers=headers, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            global _active_provider
            _active_provider = f"Groq ({model})"
            logger.info(f"Groq response OK ({len(text)} chars)")
            return text
        else:
            logger.warning(f"Groq error {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        logger.warning(f"Groq request failed: {e}")
        return None


def _try_openai(messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        model = "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        global _active_provider
        _active_provider = f"OpenAI ({model})"
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"OpenAI error: {e}")
        return None


def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> Optional[str]:
    providers = [
        ("Gemini", _try_gemini),
        ("Groq", _try_groq),
        ("OpenAI", _try_openai),
    ]

    for name, provider_fn in providers:
        result = provider_fn(messages, temperature, max_tokens)
        if result:
            logger.info(f"LLM response from {name}")
            return result

    logger.warning("All LLM providers failed or unconfigured")
    return None


def is_available() -> bool:
    return bool(
        os.environ.get("GEMINI_API_KEY", "")
        or os.environ.get("GROQ_API_KEY", "")
        or os.environ.get("OPENAI_API_KEY", "")
    )


def get_model_name() -> str:
    if _active_provider:
        return _active_provider
    if os.environ.get("GEMINI_API_KEY"):
        return "Gemini (gemini-2.0-flash)"
    if os.environ.get("GROQ_API_KEY"):
        return "Groq (llama-3.3-70b-versatile)"
    if os.environ.get("OPENAI_API_KEY"):
        return "OpenAI (gpt-4o-mini)"
    return "Aucun provider configuré"
