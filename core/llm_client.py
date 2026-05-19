"""
CoreShift LLM Client
Supports SAP AI Core (default), GROQ, Anthropic, OpenAI.

SAP AI Core fix: creates AICoreV2Client directly to avoid the
'client_type' incompatibility between generative-ai-hub-sdk 3.x
and ai-api-client-sdk 2.6+.
"""

from __future__ import annotations
import os
import time
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_DEFAULT_TEMPERATURE = 0.1
_DEFAULT_MAX_TOKENS  = 4096
_MAX_RETRIES         = 2
_RETRY_BACKOFF       = 2.0

SAP_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4",
    "gpt-35-turbo",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "claude-3-5-sonnet",
    "claude-3-opus",
    "meta--llama3-70b-instruct",
    "mistralai--mixtral-8x7b-instruct-v01",
]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

PROVIDER_LABELS = {
    "sap_ai_core": "SAP AI Core",
    "groq":        "GROQ",
    "anthropic":   "Anthropic",
    "openai":      "OpenAI",
}


class LLMClient:
    """
    Unified LLM wrapper for CoreShift.

    Usage
    ─────
    client = LLMClient()                        # SAP AI Core from .env
    client = LLMClient(provider="groq", api_key="gsk_...", model="llama-3.3-70b-versatile")
    response = client.complete("system prompt", "user message")
    """

    def __init__(self, provider: str = "sap_ai_core", **kwargs):
        self.provider = provider.lower()
        self._init_provider(**kwargs)

    # ── Initialisers ──────────────────────────────────────────────────────────

    def _init_provider(self, **kwargs):
        dispatch = {
            "sap_ai_core": self._init_sap,
            "groq":        self._init_groq,
            "anthropic":   self._init_anthropic,
            "openai":      self._init_openai,
        }
        fn = dispatch.get(self.provider)
        if not fn:
            raise ValueError(f"Unknown provider '{self.provider}'. Choose: sap_ai_core | groq | anthropic | openai")
        fn(**kwargs)

    def _init_sap(self, **kwargs):
        try:
            from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
            from gen_ai_hub.proxy.native.openai import OpenAI
            from ai_core_sdk.ai_core_v2_client import AICoreV2Client
        except ImportError:
            raise ImportError("Run: pip install generative-ai-hub-sdk")

        client_kwargs: dict = {}
        if kwargs.get("client_id"):
            client_kwargs["client_id"] = kwargs["client_id"]
        if kwargs.get("client_secret"):
            client_kwargs["client_secret"] = kwargs["client_secret"]
        if kwargs.get("auth_url"):
            client_kwargs["auth_url"] = kwargs["auth_url"]
        if kwargs.get("base_url"):
            raw = kwargs["base_url"].rstrip("/")
            client_kwargs["base_url"] = raw if raw.endswith("/v2") else f"{raw}/v2"
        if kwargs.get("resource_group"):
            client_kwargs["resource_group"] = kwargs["resource_group"]

        # Create AICoreV2Client ourselves — avoids the internal client_type arg
        # that generative-ai-hub-sdk 3.x passes but ai-api-client-sdk 2.6+ removed.
        ai_core_client      = AICoreV2Client.from_env(**client_kwargs)
        self._proxy_client  = get_proxy_client("gen-ai-hub", ai_core_client=ai_core_client)
        self._openai_client = OpenAI(proxy_client=self._proxy_client)

        self.model        = kwargs.get("model_name") or os.getenv("AICORE_MODEL", "gpt-4o")
        self.display_name = f"SAP AI Core | {self.model}"
        logger.info("SAP AI Core initialised — model: %s", self.model)

    def _init_groq(self, **kwargs):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("Run: pip install groq")
        api_key = kwargs.get("api_key") or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set.")
        self.model        = kwargs.get("model", "llama-3.3-70b-versatile")
        self._client      = Groq(api_key=api_key)
        self.display_name = f"GROQ | {self.model}"

    def _init_anthropic(self, **kwargs):
        try:
            import anthropic as _a
        except ImportError:
            raise ImportError("Run: pip install anthropic")
        api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set.")
        self.model        = kwargs.get("model", "claude-3-5-sonnet-20241022")
        self._client      = _a.Anthropic(api_key=api_key)
        self.display_name = f"Anthropic | {self.model}"

    def _init_openai(self, **kwargs):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Run: pip install openai")
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set.")
        self.model        = kwargs.get("model", "gpt-4o")
        self._client      = OpenAI(api_key=api_key)
        self.display_name = f"OpenAI | {self.model}"

    # ── Core API ──────────────────────────────────────────────────────────────

    def complete(
        self,
        system_prompt: str,
        user_message:  str,
        max_tokens:    int   = _DEFAULT_MAX_TOKENS,
        temperature:   float = _DEFAULT_TEMPERATURE,
    ) -> str:
        dispatch = {
            "sap_ai_core": self._complete_sap,
            "groq":        self._complete_groq,
            "anthropic":   self._complete_anthropic,
            "openai":      self._complete_openai,
        }
        fn, last_error = dispatch[self.provider], None
        for attempt in range(1, _MAX_RETRIES + 2):
            try:
                return fn(system_prompt, user_message, max_tokens, temperature)
            except Exception as exc:
                last_error = exc
                if attempt <= _MAX_RETRIES:
                    wait = _RETRY_BACKOFF * attempt
                    logger.warning("Attempt %d failed: %s — retrying in %.1fs", attempt, exc, wait)
                    time.sleep(wait)
        raise RuntimeError(f"LLM failed after {_MAX_RETRIES + 1} attempts. Last: {last_error}") from last_error

    def _complete_sap(self, sys_p, user_p, max_tok, temp):
        r = self._openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
            temperature=temp, max_tokens=max_tok,
        )
        return r.choices[0].message.content

    def _complete_groq(self, sys_p, user_p, max_tok, temp):
        r = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
            temperature=temp, max_tokens=max_tok,
        )
        return r.choices[0].message.content

    def _complete_anthropic(self, sys_p, user_p, max_tok, temp):
        m = self._client.messages.create(
            model=self.model, max_tokens=max_tok, temperature=temp,
            system=sys_p, messages=[{"role": "user", "content": user_p}],
        )
        return m.content[0].text

    def _complete_openai(self, sys_p, user_p, max_tok, temp):
        r = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
            temperature=temp, max_tokens=max_tok,
        )
        return r.choices[0].message.content

    def ping(self) -> str:
        return self.complete("You are a helpful assistant.", "Reply with exactly one word: OK", max_tokens=5).strip()

    def __repr__(self):
        return f"LLMClient(provider={self.provider!r}, model={self.display_name!r})"
