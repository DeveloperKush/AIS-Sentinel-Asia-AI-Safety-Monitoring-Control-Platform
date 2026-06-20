import os
import time
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai  # type: ignore
except ModuleNotFoundError as exc:
    genai = None  # type: ignore
    logger.error(
        "google-generativeai is not installed. Install it to use GeminiClient. (%s)",
        exc,
    )

GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable is not set.")

if genai is not None and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiClient:
    """
    Wrapper around Google Gemini Flash API using `google-generativeai`.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        """
        Initialize the Gemini client.

        Args:
            model_name: Gemini model name to use for generations.
        """
        self.model_name: str = model_name
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            api_key = os.environ.get("GOOGLE_API_KEY", "")
        if genai is not None and api_key:
            genai.configure(api_key=api_key)

    def _get_model(self, schema: Optional[Dict[str, Any]] = None):
        """
        Internal helper to construct a GenerativeModel.

        Args:
            schema: Optional response schema to enforce structured JSON output.

        Returns:
            Configured `genai.GenerativeModel`.

        Raises:
            RuntimeError: If the google-generativeai library is not installed.
        """
        if genai is None:
            raise RuntimeError(
                "google-generativeai is not installed. Install it to use GeminiClient."
            )

        if schema is not None:
            return genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                },
            )
        return genai.GenerativeModel(model_name=self.model_name)

    @staticmethod
    def _is_rate_limit_error(exc: BaseException) -> bool:
        """
        Best-effort detection of rate limit errors.

        Args:
            exc: Exception raised by the Gemini client.

        Returns:
            True if the error appears to be a rate limit / throttling issue.
        """
        msg = str(exc).lower()
        return any(
            s in msg
            for s in (
                "429",
                "rate limit",
                "rate-limited",
                "too many requests",
                "quota",
                "throttle",
                "throttled",
            )
        )

    def _retry(self, fn, *args, **kwargs):
        """
        Retry wrapper with exponential backoff (3 retries).

        Args:
            fn: Callable to execute.
            *args: Positional args for callable.
            **kwargs: Keyword args for callable.

        Returns:
            Result of callable.

        Raises:
            Last exception if all retries fail or if error is non-rate-limit.
        """
        retries = 3
        base_delay_s = 1.0

        last_exc: Optional[BaseException] = None
        for attempt in range(retries + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if not self._is_rate_limit_error(exc):
                    raise
                if attempt >= retries:
                    break
                delay = base_delay_s * (2 ** attempt)
                logger.warning(
                    "Gemini rate limit hit; retrying in %.2fs (attempt %d/%d). Error: %s",
                    delay,
                    attempt + 1,
                    retries,
                    exc,
                )
                time.sleep(delay)

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Retry failed without capturing exception.")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_mime_type: str = "application/json",
    ) -> str:
        """
        Generate raw text response from Gemini.

        Args:
            prompt: Input prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum output tokens.
            response_mime_type: Desired response MIME type (e.g., application/json).

        Returns:
            Raw text response (as returned by the SDK).

        Raises:
            Exception if generation fails.
        """
        def _call() -> str:
            model = self._get_model()
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            resp = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "response_mime_type": response_mime_type,
                },
                safety_settings=safety_settings
            )
            return getattr(resp, "text", None) or ""

        try:
            return self._retry(_call)
        except Exception as exc:
            logger.exception("Gemini generate failed: %s", exc)
            raise

    def generate_structured(self, prompt: str, schema: dict, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate structured JSON output enforced by a provided schema.

        Args:
            prompt: Input prompt.
            schema: JSON schema dict to enforce output structure.
            temperature: Sampling temperature.

        Returns:
            Parsed JSON object as a dict.

        Raises:
            Exception if generation or parsing fails.
        """
        def _call() -> Dict[str, Any]:
            model = self._get_model(schema=schema)
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            resp = model.generate_content(
                prompt,
                generation_config={"temperature": temperature},
                safety_settings=safety_settings
            )

            text = getattr(resp, "text", "") or ""
            try:
                # SDK typically returns already JSON-like text; parse best-effort
                import json
                return json.loads(text)
            except Exception:
                # If it's not valid JSON, return a best-effort wrapper
                return {"raw": text}

        try:
            return self._retry(_call)
        except Exception as exc:
            logger.exception("Gemini generate_structured failed: %s", exc)
            raise

    def translate(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        """
        Translate text between languages via Gemini.

        Args:
            text: Text to translate.
            source_lang: Source language (e.g., 'es', 'fr', 'en').
            target_lang: Target language (default: 'en').

        Returns:
            Translated text.
        """
        prompt = (
            "You are a translation engine. Translate the following text.\n"
            f"Source language: {source_lang}\n"
            f"Target language: {target_lang}\n"
            "Return only the translated text, with no additional commentary.\n\n"
            f"Text:\n{text}"
        )
        try:
            return self.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=2048,
                response_mime_type="text/plain",
            )
        except Exception as exc:
            logger.exception("Gemini translate failed: %s", exc)
            raise

    def count_tokens(self, text: str) -> int:
        """
        Count tokens for a given text using Gemini's tokenizer.

        Args:
            text: Text to count tokens for.

        Returns:
            Token count as an integer.

        Raises:
            Exception if counting fails.
        """
        def _call() -> int:
            model = self._get_model()
            count = model.count_tokens(text)
            try:
                return int(count.total_tokens)  # type: ignore[attr-defined]
            except Exception:
                try:
                    return int(count)  # type: ignore[call-overload]
                except Exception:
                    return 0

        try:
            return self._retry(_call)
        except Exception as exc:
            logger.exception("Gemini count_tokens failed: %s", exc)
            raise
