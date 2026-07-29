import json
import re

from fastapi import HTTPException, status
from groq import Groq

from src.app.core.config import get_settings
from src.app.schemas.voice import InstructionPayload

# Matches README / academy routing contract: endpoint + method + params only.
_SYSTEM_PROMPT = """You convert a user voice transcription into API routing JSON for a to-do list.

Reply with ONLY one JSON object. No markdown. No explanations. Exact keys:
{"endpoint":"...","method":"...","params":{...}}

Allowed routes:
- List tasks: {"endpoint":"/tasks","method":"GET","params":{}}
- Create task: {"endpoint":"/tasks","method":"POST","params":{"title":"Buy groceries"}}
  Optional params.done (boolean, default false).
- Replace task: {"endpoint":"/tasks/1","method":"PUT","params":{"title":"Buy milk","done":false}}
- Partial update: {"endpoint":"/tasks/1","method":"PATCH","params":{"done":true}}
  Or params.title only / both.
- Delete task: {"endpoint":"/tasks/1","method":"DELETE","params":{}}

Rules:
- method must be GET, POST, PUT, PATCH, or DELETE.
- Put the numeric task id in the endpoint path as /tasks/{id}. Do not invent ids that were never mentioned.
- Understand Spanish and English.
- Never return free-form text outside the JSON object.
"""

_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def route_transcription(transcription: str) -> InstructionPayload:
    """Call Groq and return routing JSON only. Does not mutate tasks."""
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
    payload = _parse_instruction_payload(raw)
    # Normalize method casing for downstream consumers / frontend.
    return InstructionPayload(
        endpoint=payload.endpoint.strip(),
        method=payload.method.upper().strip(),
        params=payload.params or {},
    )


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
