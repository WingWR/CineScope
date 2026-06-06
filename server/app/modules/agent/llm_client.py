from __future__ import annotations

import asyncio

import httpx

from server.app.core.config import AppConfig, get_config


class DeepSeekError(RuntimeError):
    pass


class DeepSeekUnavailableError(DeepSeekError):
    pass


class DeepSeekClient:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or get_config()

    def is_enabled(self) -> bool:
        return self.config.agent_use_llm and bool(self.config.deepseek_api_key)

    async def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        if not self.config.agent_use_llm:
            raise DeepSeekUnavailableError("LLM is disabled by configuration.")
        if not self.config.deepseek_api_key:
            raise DeepSeekUnavailableError("DeepSeek API key is not configured.")

        request_body = {
            "model": self.config.deepseek_model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.config.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.config.deepseek_base_url}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=self.config.deepseek_timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=request_body)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise DeepSeekError("DeepSeek request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            raise DeepSeekError(f"DeepSeek returned HTTP {exc.response.status_code}.") from exc
        except httpx.RequestError as exc:
            raise DeepSeekError("DeepSeek request failed.") from exc

        try:
            payload = response.json()
            return str(payload["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise DeepSeekError("DeepSeek returned an invalid response payload.") from exc

    def chat_sync(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.chat(messages=messages, temperature=temperature))
        raise DeepSeekUnavailableError("DeepSeek sync wrapper cannot run inside an active event loop.")
