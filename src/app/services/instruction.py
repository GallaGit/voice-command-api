import json
import re

from fastapi import HTTPException, status
from groq import Groq

from src.app.core.config import get_settings
from src.app.schemas.voice import InstructionPayload

_SYSTEM_PROMPT = """You are a routing engine for a voice-controlled to-do API.
Given a user transcription, respond with ONLY a valid JSON object (no markdown, no prose) in this exact shape:
{"endpoint":"/tasks","method":"GET|POST|PUT|PATCH|DELETE","params":{}}

Rules:
- endpoint must be "/tasks" or "/tasks/{id}" where id is an integer when targeting one task.
- method must be one of: GET, POST, PUT, PATCH, DELETE.
- For POST /tasks: params must include "title" (string). Optional "done" (boolean, default false).
- For PUT /tasks/{id}: params must include "title" (string) and "done" (boolean). Put the id in the endpoint path.
- For PATCH /tasks/{id}: params may include "title" and/or "done". Put the id in the endpoint path.
- For DELETE /tasks/{id}: params may be {}. Put the id in the endpoint path.
- For GET /tasks: params may be {}.
- Infer intent from the user's language (Spanish or English). Never invent free-form text outside the JSON object.
"""

_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def route_transcription(transcription: str) -> InstructionPayload:
    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)

    try:
        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": transcription},
            ],
            temperature=0,
            response_format={"type": "json_object"},
            timeout=settings.request_timeout_seconds,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq instruction routing failed: {exc}",
        ) from exc

    raw = (completion.choices[0].message.content or "").strip()
    return _parse_instruction_payload(raw)


def _parse_instruction_payload(raw: str) -> InstructionPayload:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = _JSON_OBJECT_RE.search(raw)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Groq did not return valid JSON for instruction routing.",
            )
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Groq returned unparseable JSON for instruction routing.",
            ) from exc

    try:
        return InstructionPayload.model_validate(data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq JSON did not match InstructionPayload: {exc}",
        ) from exc
