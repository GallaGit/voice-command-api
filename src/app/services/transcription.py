from fastapi import HTTPException, UploadFile, status
from groq import Groq

from src.app.core.config import get_settings


async def transcribe_audio(file: UploadFile, language: str | None = None) -> str:
    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty audio file.",
        )

    filename = file.filename or "audio.webm"
    kwargs: dict = {
        "file": (filename, content, file.content_type or "application/octet-stream"),
        "model": settings.groq_transcription_model,
        "timeout": settings.request_timeout_seconds,
    }
    if language:
        kwargs["language"] = language

    try:
        result = client.audio.transcriptions.create(**kwargs)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq transcription failed: {exc}",
        ) from exc

    text = (getattr(result, "text", None) or "").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq returned an empty transcription.",
        )
    return text
