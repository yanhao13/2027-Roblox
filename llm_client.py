"""Production LLM driver routing MATCHA agent operations to the DeepSeek API
(deepseek-v4-pro), which exposes an OpenAI-compatible chat/completions endpoint.

Note: deepseek-v4-pro is a reasoning model. Its responses carry a separate
``reasoning_content`` field alongside the final ``content``; we read only the
final ``content`` and budget max_tokens generously so reasoning does not starve
the answer.
"""
import os
import httpx


class DeepSeekPipelineClient:
    """Production LLM driver interface wrapping MATCHA agent operations to the
    live DeepSeek API engine (deepseek-v4-pro)."""

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "[!] Critical Initialization Error: DEEPSEEK_API_KEY environment variable missing."
            )
        self.model_target = "deepseek-v4-pro"
        self.base_url = "https://api.deepseek.com/chat/completions"

    def _post(self, system_instruction: str, user_prompt: str, max_tokens: int) -> str:
        """Single completion round-trip. Reads the final ``content`` field."""
        payload = {
            "model": self.model_target,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        resp = httpx.post(self.base_url, json=payload, headers=headers, timeout=180.0)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"].get("content") or ""

    def _call_llm(self, prompt: str, system_instruction: str = "You are a professional assistant.") -> str:
        """Standard completions generator for conversational, reflection, and safety checks."""
        return self._post(system_instruction, prompt, max_tokens=2048)

    def _call_structured_llm(self, system_instruction: str, user_prompt: str) -> str:
        """Enforces raw JSON schema alignment via structured prompt criteria formatting."""
        formatting_directive = (
            "\n\nCRITICAL: Return ONLY a valid JSON string object matching the schema requested. "
            "Do not include introductory text, conversational pleasantries, or markdown blocks."
        )
        return self._post(system_instruction, user_prompt + formatting_directive, max_tokens=4096)

    def _call_generation_api(self, system_instruction: str, user_prompt: str) -> str:
        """Maps directly over internal pipeline calls handling localized summary generation."""
        return self._call_llm(prompt=user_prompt, system_instruction=system_instruction)
