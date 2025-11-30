"""
Gemini-based multimodal fact checker service.
"""
from __future__ import annotations

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types


logger = logging.getLogger("truetrace.multimodal")


def _extract_rating_line(text: str) -> Optional[str]:
    """
    Try to extract the verdict sentence from the analysis text.
    """
    keywords = ("verified", "misleading", "false", "satire", "partly", "uncertain")
    for line in text.splitlines():
        normalized = line.strip().lower()
        if any(keyword in normalized for keyword in keywords):
            return line.strip()
    return None


class MultimodalFactChecker:
    """
    Helper around the Gemini SDK to analyze multimodal (file + text) inputs.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_prompt: str,
        poll_interval: float = 2.0,
        poll_timeout: int = 180,
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required for the multimodal fact checker.")

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.base_prompt = base_prompt.strip()
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout

    def _write_temp_file(self, filename: str, data: bytes) -> str:
        suffix = Path(filename or "upload.bin").suffix or ".bin"
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(data)
        logger.debug("Saved temporary upload to %s (%s bytes)", path, len(data))
        return path

    def _upload_and_wait(self, path: str) -> types.File:
        uploaded = self.client.files.upload(file=path)
        logger.debug("Uploaded file to Gemini: %s (state=%s)", uploaded.name, uploaded.state.name)

        start = time.time()
        while uploaded.state.name == "PROCESSING":
            elapsed = time.time() - start
            if elapsed > self.poll_timeout:
                raise TimeoutError("Timed out waiting for Gemini to process the file.")
            time.sleep(self.poll_interval)
            uploaded = self.client.files.get(name=uploaded.name)
            logger.debug("Polling Gemini file (%s) state=%s", uploaded.name, uploaded.state.name)

        if uploaded.state.name == "FAILED":
            raise ValueError("Gemini reported a failure while processing the uploaded file.")

        return uploaded

    def analyze(
        self,
        *,
        filename: Optional[str],
        file_bytes: Optional[bytes],
        user_text: Optional[str],
        context: Optional[str],
        delete_remote_file: bool = True,
    ) -> Dict[str, Any]:
        if not file_bytes and not (user_text and user_text.strip()):
            raise ValueError("Please provide a file or supplemental text to analyze.")

        temp_path: Optional[str] = None
        uploaded_file: Optional[types.File] = None
        file_metadata: Optional[Dict[str, Any]] = None
        content_parts: List[Any] = []

        if self.base_prompt:
            content_parts.append(self.base_prompt)

        if context and context.strip():
            content_parts.append(context.strip())

        try:
            if file_bytes:
                temp_path = self._write_temp_file(filename or "fact-check-upload.bin", file_bytes)
                uploaded_file = self._upload_and_wait(temp_path)
                content_parts.append(uploaded_file)
                file_metadata = {
                    "name": uploaded_file.name,
                    "display_name": getattr(uploaded_file, "display_name", filename),
                    "mime_type": getattr(uploaded_file, "mime_type", None),
                    "state": uploaded_file.state.name if uploaded_file.state else None,
                    "size_bytes": getattr(uploaded_file, "size_bytes", None),
                }

            if user_text and user_text.strip():
                content_parts.append(user_text.strip())

            logger.debug(
                "Submitting %s content parts to Gemini model %s",
                len(content_parts),
                self.model,
            )

            start = time.time()
            response = self.client.models.generate_content(
                model=self.model,
                contents=content_parts,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_modalities=["TEXT"],
                    temperature=0.2,
                ),
            )
            latency_ms = int((time.time() - start) * 1000)
            logger.debug("Gemini multimodal analysis completed in %sms", latency_ms)

            analysis_text = (response.text or "").strip()
            if not analysis_text and response.candidates:
                # Fallback to concatenating candidate parts.
                candidate_text = []
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        candidate_text.append(part.text)
                analysis_text = "\n".join(candidate_text).strip()

            if not analysis_text:
                analysis_text = "Gemini returned no textual analysis."

            sources = self._extract_sources(response)

            return {
                "model": self.model,
                "analysis_text": analysis_text,
                "verdict_summary": _extract_rating_line(analysis_text),
                "sources": sources,
                "file": file_metadata,
                "latency_ms": latency_ms,
                "used_google_search": True,
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            if delete_remote_file and uploaded_file is not None:
                try:
                    self.client.files.delete(name=uploaded_file.name)
                    logger.debug("Deleted Gemini uploaded file %s", uploaded_file.name)
                except Exception as exc:  # pragma: no cover - best-effort cleanup
                    logger.warning("Failed to delete Gemini file %s: %s", uploaded_file.name, exc)

    def _extract_sources(self, response: Any) -> Optional[Dict[str, Any]]:
        if not response.candidates:
            return None

        candidate = response.candidates[0]
        grounding = getattr(candidate, "grounding_metadata", None)
        if not grounding:
            return None

        rendered_content = None
        references: List[Dict[str, Any]] = []

        search_entry = getattr(grounding, "search_entry_point", None)
        if search_entry:
            rendered_content = getattr(search_entry, "rendered_content", None)

        chunks = getattr(grounding, "grounding_chunks", None) or []
        for chunk in chunks:
            references.append(
                {
                    "id": getattr(chunk, "id", None),
                    "title": getattr(chunk, "title", None),
                    "snippet": getattr(chunk, "content", None),
                    "uri": getattr(chunk, "uri", None),
                }
            )

        if not rendered_content and not references:
            return None

        return {
            "rendered_content": rendered_content,
            "references": references or None,
        }

