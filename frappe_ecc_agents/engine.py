"""
Frappe ECC LLM Engine & Claude Integration Interface
Connects all 53 Frappe AI Agents directly with Anthropic Claude (Claude 3.5 Sonnet / Claude 3.7 Sonnet).
Supports persistent API key management, model routing, and end-to-end autonomous app architecture synthesis.
"""

import os
import sys
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger("frappe_ecc_agents.engine")

KEY_STORAGE_PATH = os.path.join(os.path.expanduser("~"), ".claude_key")
ENV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


class LLMEngine:
    """Unified Claude AI Engine for Frappe ECC Autonomous Agents."""

    _active_key: Optional[str] = None
    _active_model: str = "claude-3-5-sonnet-20241022"

    @classmethod
    def get_claude_key(cls) -> Optional[str]:
        """Resolves Claude API key from memory, environment, or persistent key files."""
        if cls._active_key:
            return cls._active_key

        # 1. Environment variable
        env_key = os.getenv("ANTHROPIC_API_KEY")
        if env_key and env_key.strip():
            cls._active_key = env_key.strip()
            return cls._active_key

        # 2. Local config file (~/.claude_key)
        if os.path.exists(KEY_STORAGE_PATH):
            try:
                with open(KEY_STORAGE_PATH, "r", encoding="utf-8") as f:
                    stored_key = f.read().strip()
                    if stored_key:
                        cls._active_key = stored_key
                        os.environ["ANTHROPIC_API_KEY"] = stored_key
                        return cls._active_key
            except Exception:
                pass

        # 3. Repository .env file
        if os.path.exists(ENV_FILE_PATH):
            try:
                with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("ANTHROPIC_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                cls._active_key = val
                                os.environ["ANTHROPIC_API_KEY"] = val
                                return cls._active_key
            except Exception:
                pass

        return None

    @classmethod
    def set_claude_key(cls, api_key: str, model: str = "claude-3-5-sonnet-20241022") -> bool:
        """Sets and persists the Claude API key across sessions."""
        api_key = api_key.strip()
        if not api_key:
            return False

        cls._active_key = api_key
        cls._active_model = model
        os.environ["ANTHROPIC_API_KEY"] = api_key

        # Save to ~/.claude_key
        try:
            with open(KEY_STORAGE_PATH, "w", encoding="utf-8") as f:
                f.write(api_key)
        except Exception as e:
            logger.warning(f"Could not persist key to {KEY_STORAGE_PATH}: {e}")

        # Save to .env
        try:
            with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(f"ANTHROPIC_API_KEY={api_key}\n")
        except Exception:
            pass

        return True

    @classmethod
    def get_active_model(cls) -> str:
        return cls._active_model

    @classmethod
    def set_active_model(cls, model_name: str) -> None:
        cls._active_model = model_name

    @classmethod
    def get_masked_key(cls) -> str:
        key = cls.get_claude_key()
        if not key:
            return ""
        if len(key) <= 10:
            return "sk-ant-***"
        return f"{key[:8]}...{key[-4:]}"

    @classmethod
    def verify_connection(cls, test_key: Optional[str] = None) -> Dict[str, Any]:
        """Tests live connectivity to Anthropic Claude API."""
        key = test_key or cls.get_claude_key()
        masked = cls.get_masked_key() if not test_key else (f"{test_key[:8]}...{test_key[-4:]}" if len(test_key) > 10 else "sk-ant-***")
        if not key:
            return {
                "connected": False,
                "masked_key": "",
                "model": cls._active_model,
                "message": "No Anthropic Claude API key configured."
            }

        try:
            req_data = json.dumps({
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "ping"}]
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=req_data,
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    return {
                        "connected": True,
                        "masked_key": masked,
                        "model": cls._active_model,
                        "message": "Connected to Anthropic Claude API successfully!"
                    }
        except urllib.error.HTTPError as e:
            return {
                "connected": False,
                "masked_key": masked,
                "model": cls._active_model,
                "message": f"Claude API Error (HTTP {e.code}): {e.reason}"
            }
        except Exception as e:
            return {
                "connected": False,
                "masked_key": masked,
                "model": cls._active_model,
                "message": f"Connection check failed: {str(e)}"
            }

        return {"connected": False, "masked_key": masked, "model": cls._active_model, "message": "Verification failed"}

    @classmethod
    def complete(
        cls,
        prompt: str,
        system_prompt: str = "You are an expert Frappe Framework autonomous developer.",
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4000
    ) -> str:
        """Sends request to Anthropic Claude API."""
        key = cls.get_claude_key()
        if not key:
            return ""

        active_model = model or cls._active_model or "claude-3-5-sonnet-20241022"

        try:
            req_data = json.dumps({
                "model": active_model,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=req_data,
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["content"][0]["text"]
        except Exception as e:
            logger.warning(f"Claude API call failed: {e}. Falling back to autonomous synthesizer.")
            return ""


class ClaudeAppArchitect:
    """Uses Claude to design and architect custom software applications from scratch on Frappe Framework."""

    SYSTEM_PROMPT = """You are the Principal Autonomous AI Software Architect and Frappe Core Developer.
Your mission is to architect and synthesize a 100% complete, customized enterprise software application from scratch on top of the Frappe Framework based on the user's idea.
DO NOT use hardcoded templates or generic placeholders. Create a bespoke domain model tailored strictly to the prompt.

You MUST output ONLY a valid JSON object matching this exact schema:
{
  "app_name": "unique_snake_case_name",
  "app_title": "Clean Human Readable Title",
  "app_description": "Precise summary of what this software does",
  "primary_doctype": "Primary Entity Name (e.g. Patient Consultation, Cargo Booking, Loan Application)",
  "autoname_prefix": "3-4 letter uppercase prefix like MED-, FLEET-, LEASE-",
  "fields": [
    {
      "fieldname": "snake_case_fieldname",
      "fieldtype": "Data | Select | Currency | Date | Datetime | Float | Int | Check | Text Editor",
      "label": "Human Label",
      "reqd": 0 or 1,
      "options": "Options for Select newline separated, or Link DocType"
    }
  ],
  "workflow_states": ["Draft", "Under Review", "Approved", "Rejected", "Completed"],
  "simulated_records": [
    {
      "fieldname_1": "realistic value 1",
      "fieldname_2": "realistic value 2",
      "requested_amount": 12500.0,
      "status": "Draft | Under Review | Approved"
    }
  ],
  "working_sop_markdown": "Full Markdown Standard Operating Procedure with steps and role instructions"
}
"""

    @classmethod
    def generate_from_claude(cls, prompt_text: str, simulated_count: int = 25) -> Optional[Dict[str, Any]]:
        """Invokes Claude to construct the complete software specification from scratch."""
        user_prompt = f"""Architect a complete custom software application on the Frappe Framework for the following requirement:
Prompt: "{prompt_text}"

Include {simulated_count} realistic, domain-specific simulated records matching the fields.
Respond ONLY with the raw JSON object, without markdown code fences or conversational text.
"""
        response_text = LLMEngine.complete(
            prompt=user_prompt,
            system_prompt=cls.SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=4000
        )

        if not response_text:
            return None

        # Clean JSON fences if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:].strip()
        elif text.startswith("```"):
            text = text[3:].strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        try:
            spec = json.loads(text)
            if "primary_doctype" in spec and "fields" in spec:
                return spec
        except Exception as e:
            logger.warning(f"Failed to parse Claude JSON response: {e}")

        return None


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
