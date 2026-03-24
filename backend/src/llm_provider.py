# -*- coding: utf-8 -*-
"""
LLM Provider - Wrapper unifie pour les appels LLM
Moteur de Rédaction Magique v5.0

Utilise OpenAI API avec fallback gracieux.
"""

import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"


def _get_client():
    try:
        import openai
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return None
        return openai.OpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        return None


def chat_completion(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> Optional[str]:
    client = _get_client()
    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None


def is_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", ""))


def get_model_name() -> str:
    return DEFAULT_MODEL
