import os
import uuid

from fastapi import HTTPException, UploadFile

from app.config import get_settings
from app.logging_conf import get_logger

log = get_logger(__name__)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
DOCUMENT_EXTENSIONS = {".docx", ".pdf", ".txt", ".csv"}


def new_session_id() -> str:
    return uuid.uuid4().hex[:12]


def safe_filename(filename: str | None, fallback: str = "upload") -> str:
    """Strip any directory component so uploads cannot escape the upload dir."""
    if not filename:
        return fallback
    name = os.path.basename(filename.replace("\\", "/")).strip()
    return name or fallback


async def save_upload(
    upload: UploadFile,
    session_id: str,
    allowed_extensions: set[str],
) -> str:
    settings = get_settings()
    name = safe_filename(upload.filename)
    ext = os.path.splitext(name)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(allowed_extensions)}",
        )

    payload = await upload.read()
    if len(payload) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.max_upload_bytes} bytes.",
        )

    os.makedirs(settings.upload_dir, exist_ok=True)
    dest = os.path.join(settings.upload_dir, f"{session_id}_{name}")

    with open(dest, "wb") as fh:
        fh.write(payload)

    return dest


async def save_images(images, session_id: str) -> list[str]:
    saved: list[str] = []
    for image in images or []:
        if not image or not image.filename:
            continue
        saved.append(await save_upload(image, session_id, IMAGE_EXTENSIONS))
    return saved


def build_contexts(
    dom_inspector,
    vision_handler,
    environment: str,
    dom_inspection: bool,
    image_paths: list[str],
    headless: bool = True,
):
    """Collect optional DOM and screenshot context shared by all intake endpoints."""
    settings = get_settings()
    dom_context = None
    dom_data = None
    image_context = None
    vision_result = None

    if dom_inspection:
        dom_data = _safe_dom(dom_inspector, settings.resolve_url(environment), headless)
        if dom_data and dom_data.get("success"):
            dom_context = dom_inspector.format_dom_context(dom_data)

    if image_paths:
        vision_result = vision_handler.analyze_images(image_paths)
        if dom_data is None:
            dom_data = _safe_dom(dom_inspector, settings.resolve_url(environment), headless)
        image_context = vision_handler.format_image_context(vision_result, dom_data)

    return dom_context, dom_data, image_context, vision_result


def _safe_dom(dom_inspector, url: str, headless: bool):
    """DOM inspection is best-effort; a failure must not abort test generation."""
    try:
        return dom_inspector.extract_dom(url, headless=headless)
    except Exception:
        log.warning("DOM inspection failed for %s; continuing without it", url, exc_info=True)
        return None
