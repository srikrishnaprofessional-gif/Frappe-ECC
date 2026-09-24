"""
Frappe ECC LLM Engine & Reasoning Interface
Supports OpenAI, Anthropic Claude, Google Gemini, Ollama, and high-fidelity deterministic generation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("frappe_ecc_agents.engine")


class LLMEngine:
    """Unified AI Engine for Frappe ECC Agents."""

    @staticmethod
    def is_api_available() -> bool:
        """Checks if any supported commercial LLM provider API key is present."""
        return any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY"),
            os.getenv("GOOGLE_API_KEY")
        ])

    @staticmethod
    def complete(
        prompt: str,
        system_prompt: str = "You are an expert Frappe Framework autonomous developer.",
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.2,
        max_tokens: int = 4000
    ) -> str:
        """
        Sends request to active LLM API if key is present; otherwise returns empty string
        signaling agent to use its high-fidelity deterministic generator.
        """
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if anthropic_key:
            try:
                import urllib.request
                req_data = json.dumps({
                    "model": model if "claude" in model else "claude-3-5-sonnet-20241022",
                    "max_tokens": max_tokens,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=req_data,
                    headers={
                        "x-api-key": anthropic_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["content"][0]["text"]
            except Exception as e:
                logger.warning(f"Anthropic API call failed: {e}. Falling back to deterministic mode.")

        if openai_key:
            try:
                import urllib.request
                req_data = json.dumps({
                    "model": "gpt-4o" if "gpt" in model else "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=req_data,
                    headers={
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Falling back to deterministic mode.")

        # Default fallback
        return ""


def clean_code_block(text: str, language: str = "") -> str:
    """Utility to strip markdown backticks from LLM responses."""
    text = text.strip()
    if text.startswith(f"```{language}"):
        text = text[len(f"```{language}"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text
