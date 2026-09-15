import json
from typing import Any, Dict, List, Optional, Protocol, Type
from pydantic import BaseModel
import httpx
from app.core.config import settings
from app.core.logging import logger


class LLMProvider(Protocol):
    async def generate(
        self,
        messages: List[Dict[str, str]],
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Any:
        ...


class GeminiProvider:
    """
    Real Google Gemini LLM provider adapter using google-generativeai.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured. Real LLM credentials are required.")
        self.model_name = model_name or settings.LLM_MODEL or "gemini-1.5-flash"
        
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model_name)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Any:
        import google.generativeai as genai

        # Format system & user prompt
        system_instruction = ""
        prompt_parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                system_instruction += content + "\n\n"
            else:
                prompt_parts.append(f"{role.upper()}:\n{content}")

        full_prompt = "\n\n".join(prompt_parts)
        if system_instruction:
            full_prompt = f"SYSTEM INSTRUCTIONS:\n{system_instruction}\n\nUSER PROMPT:\n{full_prompt}"

        if schema:
            json_schema_str = json.dumps(schema.model_json_schema(), indent=2)
            full_prompt += (
                f"\n\nCRITICAL REQUIREMENT: You MUST respond ONLY with a valid JSON object matching this schema. "
                f"Do not include markdown codeblocks or extra text:\n{json_schema_str}"
            )

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json" if schema else "text/plain",
        )

        try:
            response = await self.client.generate_content_async(
                full_prompt,
                generation_config=generation_config,
            )
            raw_text = response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API invocation failed: {e}")
            raise RuntimeError(f"Gemini generation error: {e}") from e

        if schema:
            # Strip potential ```json ``` wraps if any
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`").strip()
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:].strip()
            try:
                parsed_json = json.loads(raw_text)
                return schema.model_validate(parsed_json)
            except Exception as e:
                logger.error(f"Failed to validate Gemini output against {schema.__name__}: {e}. Raw: {raw_text[:200]}")
                raise ValueError(f"Model response did not conform to schema {schema.__name__}: {e}") from e

        return raw_text


class OpenAIProvider:
    """
    Real OpenAI LLM provider adapter using the official openai SDK.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured. Real LLM credentials are required.")
        self.model_name = model_name or settings.LLM_MODEL or "gpt-4o"
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Any:
        try:
            if schema:
                # Use structured outputs
                completion = await self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=messages,
                    response_format=schema,
                    temperature=temperature,
                )
                return completion.choices[0].message.parsed
            else:
                completion = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                )
                return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API invocation failed: {e}")
            raise RuntimeError(f"OpenAI generation error: {e}") from e


class OllamaProvider:
    """
    Real local Ollama LLM provider adapter.
    """
    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model_name = model_name or settings.OLLAMA_MODEL or "llama3"

    async def generate(
        self,
        messages: List[Dict[str, str]],
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Any:
        url = f"{self.base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if schema:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_text = data.get("message", {}).get("content", "").strip()
            except Exception as e:
                logger.error(f"Ollama local API invocation failed: {e}")
                raise RuntimeError(f"Ollama generation error: {e}") from e

        if schema:
            parsed = json.loads(raw_text)
            return schema.model_validate(parsed)

        return raw_text


def get_llm_provider() -> LLMProvider:
    """
    Factory returning the configured real LLM provider.
    Explicitly checks provider configuration; never returns a dummy.
    """
    provider_name = (settings.LLM_PROVIDER or "gemini").lower()

    if provider_name == "gemini":
        if not settings.GEMINI_API_KEY:
            # Check if OPENAI_API_KEY exists to provide helpful guidance
            if settings.OPENAI_API_KEY:
                logger.info("GEMINI_API_KEY not found, using configured OPENAI_API_KEY.")
                return OpenAIProvider()
            raise ValueError(
                "GEMINI_API_KEY is not set in environment or .env. "
                "Please configure GEMINI_API_KEY or set LLM_PROVIDER=openai with OPENAI_API_KEY."
            )
        return GeminiProvider()

    elif provider_name == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment or .env.")
        return OpenAIProvider()

    elif provider_name == "ollama":
        return OllamaProvider()

    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
