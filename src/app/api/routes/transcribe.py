from fastapi import APIRouter, HTTPException, Request, status

from src.app.schemas.voice import TranscribeFlowResponse
from src.app.services.executor import execute_instruction
from src.app.services.instruction import route_transcription
from src.app.services.transcription import transcribe_audio
from src.app.utils.language import normalize_transcription_language

router = APIRouter(tags=["transcribe"])


@router.get("/")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/transcribe", response_model=TranscribeFlowResponse)
async def transcribe_and_run_flow(request: Request) -> TranscribeFlowResponse:
    content_type = (request.headers.get("content-type") or "").lower()

    if "application/json" in content_type:
        body = await request.json()
        if not isinstance(body, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON body must be an object with 'transcription'.",
            )
        transcription = str(body.get("transcription") or "").strip()
        if not transcription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field 'transcription' is required.",
            )
    elif "multipart/form-data" in content_type:
        form = await request.form()
        upload = form.get("file")
        if upload is None or not hasattr(upload, "read"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multipart field 'file' is required for audio transcription.",
            )
        lang = normalize_transcription_language(form.get("language"))
        transcription = await transcribe_audio(upload, language=lang)
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Use multipart/form-data with 'file' or application/json with 'transcription'.",
        )

    instruction = route_transcription(transcription)
    result = execute_instruction(instruction)
    return TranscribeFlowResponse(
        transcription=transcription,
        instruction=instruction,
        result=result,
    )
