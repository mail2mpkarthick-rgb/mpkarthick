import os
import json
import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, HealingRecord, AutoFixDiffLog, WorkflowSession
from app.agent import GeminiAgent
from app.generator import CodeScaffolder
from app.executor import TestExecutor
from app.healer import SelfHealer
from app.parser import DocumentParser
from app.reporter import ReportGenerator
from app.dom_inspector import DOMInspector
from app.pom_repository import POMRepository
from app.vision_handler import VisionHandler
from app.logging_conf import configure_logging, get_logger
from app.config import get_settings
from app.services import intake
from app.services.validator import UnsafeGeneratedCode

settings = get_settings()
configure_logging(settings.log_level)
log = get_logger(__name__)

app = FastAPI(title="G_Automation_AI v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def resolve_env(env: str) -> str:
    """Resolve short environment name to full domain URL."""
    return settings.resolve_host(env)


def resolve_url(env: str) -> str:
    """Resolve short environment name to full URL."""
    return settings.resolve_url(env)


@app.exception_handler(UnsafeGeneratedCode)
def unsafe_code_handler(request, exc: UnsafeGeneratedCode):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


def _generate_manual_tests_or_fail(
    input_text: str,
    input_type: str,
    environment: str,
    dom_context=None,
    image_context=None,
) -> str:
    """Generate manual test cases, failing loudly rather than substituting placeholders."""
    try:
        manual_tests = agent.generate_manual_tests(
            input_text,
            input_type=input_type,
            environment=environment,
            dom_context=dom_context,
            image_context=image_context,
        )
    except Exception as e:
        log.exception("Gemini test generation failed (input_type=%s)", input_type)
        detail = f"AI test generation failed: {e}"
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            detail = (
                "Gemini API quota exceeded. The free tier allows only 20 requests/day "
                "for this model. Enable billing on your API key or wait for the quota "
                "to reset, then retry."
            )
        raise HTTPException(status_code=502, detail=detail) from e

    try:
        parsed = json.loads(manual_tests)
    except json.JSONDecodeError as e:
        log.error(
            "Model returned non-JSON test cases (input_type=%s): %.800s",
            input_type,
            manual_tests,
        )
        raise HTTPException(
            status_code=502,
            detail=f"AI returned malformed test cases: {e}",
        ) from e

    if not isinstance(parsed, list) or not parsed:
        log.error("Model returned empty/invalid test case list: %.800s", manual_tests)
        raise HTTPException(
            status_code=502,
            detail="AI returned no usable test cases. Try rephrasing the scenario.",
        )

    return manual_tests


# Initialize all components
agent = GeminiAgent(
    test_gen_model=settings.test_gen_model,
    code_gen_model=settings.code_gen_model,
    vision_model=settings.vision_model,
    timeout=settings.gemini_timeout,
    max_retries=settings.gemini_max_retries,
)
scaffolder = CodeScaffolder()
executor = TestExecutor(workspace_path=settings.workspace_dir)
healer = SelfHealer(agent, scaffolder)
reporter = ReportGenerator()
dom_inspector = DOMInspector()
pom_repo = POMRepository()
vision_handler = VisionHandler(agent, dom_inspector)

UPLOAD_DIR = settings.upload_dir
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ───────────────────────────────
STATIC_DIR = settings.static_dir
os.makedirs(STATIC_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_path = os.path.join(STATIC_DIR, "index.html")

    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return HTMLResponse(
        "<h1>G_Automation_AI v2</h1>"
        "<p>Frontend not found. Run the application from the project root.</p>"
    )


@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    return serve_frontend()


# ───────────────────────────────
#  API Endpoints
# ───────────────────────────────


@app.post("/workflow/from-prompt")
async def workflow_from_prompt(
    prompt: str = Form(...),
    environment: str = Form("dev.ges.store"),
    data_mode: str = Form("inline"),
    retry_cap: int = Form(3),
    dom_inspection: str = Form("false"),
    browser_mode: str = Form("headless"),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Step 1a: Generate manual test cases from a user prompt with environment & image support."""

    if len(prompt) > settings.max_prompt_chars:
        raise HTTPException(
            status_code=400,
            detail=f"Prompt exceeds {settings.max_prompt_chars} characters.",
        )

    session_id = intake.new_session_id()
    headless = browser_mode != "headed"

    image_paths = await intake.save_images(images, session_id)

    dom_context, dom_data, image_context, vision_result = intake.build_contexts(
        dom_inspector,
        vision_handler,
        environment=environment,
        dom_inspection=dom_inspection == "true",
        image_paths=image_paths,
        headless=headless,
    )

    manual_tests = _generate_manual_tests_or_fail(
        prompt,
        input_type="prompt",
        environment=environment,
        dom_context=dom_context,
        image_context=image_context,
    )

    session = WorkflowSession(
        session_id=session_id,
        input_type="prompt",
        input_content=prompt,
        manual_test_cases=manual_tests,
        environment=environment,
        data_mode=data_mode,
        retry_cap=retry_cap,
        image_paths=json.dumps(image_paths)
        if image_paths
        else None,
        dom_context=json.dumps(dom_data)
        if dom_inspection == "true" and dom_data
        else None,
        user_confirmed=False,
        execution_status="pending"
    )

    db.add(session)
    db.commit()

    return {
        "session_id": session_id,
        "manual_test_cases": json.loads(manual_tests),
        "environment": environment,
        "data_mode": data_mode,
        "retry_cap": retry_cap,
        "dom_inspected": dom_context is not None,
        "images_analyzed": len(image_paths)
        if image_paths
        else 0,
        "image_warnings": vision_result.get("warnings", [])
        if image_context
        else []
    }


@app.post("/workflow/from-document")
async def workflow_from_document(
    file: UploadFile = File(...),
    environment: str = Form("dev.ges.store"),
    data_mode: str = Form("inline"),
    retry_cap: int = Form(3),
    dom_inspection: str = Form("false"),
    browser_mode: str = Form("headless"),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Step 1b: Upload a document (Word/PDF/TXT/CSV) and generate manual test cases."""

    session_id = intake.new_session_id()
    headless = browser_mode != "headed"

    filepath = await intake.save_upload(
        file, session_id, intake.DOCUMENT_EXTENSIONS
    )

    parsed = DocumentParser.parse_document(filepath)

    extracted_text = parsed.get("text", "")
    embedded_images = parsed.get("embedded_images", [])

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text found in the document. "
                f"Parser reported: {parsed.get('error') or 'empty content'}"
            ),
        )

    uploaded_image_paths = await intake.save_images(images, session_id)
    all_image_paths = embedded_images + uploaded_image_paths

    dom_context, dom_data, image_context, vision_result = intake.build_contexts(
        dom_inspector,
        vision_handler,
        environment=environment,
        dom_inspection=dom_inspection == "true",
        image_paths=all_image_paths,
        headless=headless,
    )

    manual_tests = _generate_manual_tests_or_fail(
        extracted_text,
        input_type="document",
        environment=environment,
        dom_context=dom_context,
        image_context=image_context,
    )

    session = WorkflowSession(
        session_id=session_id,
        input_type="document",
        input_content=extracted_text,
        document_filename=filename,
        manual_test_cases=manual_tests,
        environment=environment,
        data_mode=data_mode,
        retry_cap=retry_cap,
        image_paths=json.dumps(all_image_paths)
        if all_image_paths
        else None,
        dom_context=json.dumps(dom_data)
        if dom_inspection == "true" and dom_data
        else None,
        user_confirmed=False,
        execution_status="pending"
    )

    db.add(session)
    db.commit()

    return {
        "session_id": session_id,
        "manual_test_cases": json.loads(
            manual_tests
        ),
        "environment": environment,
        "data_mode": data_mode,
        "retry_cap": retry_cap,
        "dom_inspected": dom_context is not None,
        "images_analyzed": len(all_image_paths),
        "extracted_text_preview": (
            extracted_text[:500] + "..."
            if len(extracted_text) > 500
            else extracted_text
        )
    }


@app.post("/workflow/confirm")
def confirm_workflow(
    session_id: str = Form(...),
    edited_test_cases: str = Form(None),
    db: Session = Depends(get_db)
):
    """Step 2: User confirms (and optionally edits) manual test cases → generates POM scripts."""

    session = (
        db.query(WorkflowSession)
        .filter(
            WorkflowSession.session_id == session_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Use user-edited test cases if provided
    if edited_test_cases:

        try:
            json.loads(edited_test_cases)

            session.manual_test_cases = (
                edited_test_cases
            )

        except json.JSONDecodeError:

            raise HTTPException(
                status_code=400,
                detail="Invalid edited test cases JSON"
            )

    session.user_confirmed = True
    session.execution_status = "generating"

    db.commit()

    try:

        # Get existing POM context for reuse
        existing_pom_code = (
            scaffolder.get_existing_pom_context()
        )

        # Get DOM context if available
        dom_context = None

        if session.dom_context:

            try:

                dom_data = json.loads(
                    session.dom_context
                )

                dom_context = (
                    dom_inspector.format_dom_context(
                        dom_data
                    )
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):
                pass

        pom_result = agent.generate_pom_scripts(
            session.manual_test_cases,
            environment=session.environment
            or "dev.ges.store",
            dom_context=dom_context,
            existing_pom_code=existing_pom_code,
            data_mode=session.data_mode
            or "inline",
            data_source_path=None
        )

        page_code = pom_result.get(
            "page_code",
            ""
        )

        test_code = pom_result.get(
            "test_code",
            ""
        )

        if not page_code and test_code:

            page_code = """// Page Object for automated tests
class AppPage {
    constructor(page) {
        this.page = page;
    }

    async navigate(url) {
        await this.page.goto(url);
    }

    async fillInput(selector, value) {
        await this.page.fill(selector, value);
    }

    async clickElement(selector) {
        await this.page.click(selector);
    }

    async getText(selector) {
        return this.page.textContent(selector);
    }
}

module.exports = { AppPage };"""

        test_name = f"test_{session_id}"

        page_path = (
            scaffolder.save_page_object(
                f"{test_name}_page",
                page_code
            )
        )

        test_path = scaffolder.save_test(
            test_name,
            test_code
        )

        # Propose new locators for repository
        new_locators = (
            scaffolder.propose_new_locators(
                test_code + page_code
            )
        )

        session.pom_script_code = test_code
        session.pom_page_code = page_code
        session.execution_status = "scripts_ready"

        db.commit()

        return {
            "status": "scripts_generated",
            "session_id": session_id,
            "test_name": test_name,
            "page_path": page_path,
            "test_path": test_path,
            "page_code": page_code,
            "test_code": test_code,
            "proposed_locators": new_locators
        }

    except Exception as e:

        session.execution_status = "error"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Script generation failed: {str(e)}"
        )


@app.post("/workflow/execute")
def execute_workflow(
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Step 3: Execute tests, classify failure, auto-heal if script issue, re-execute, generate report."""

    session = (
        db.query(WorkflowSession)
        .filter(
            WorkflowSession.session_id == session_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    test_name = f"test_{session_id}"

    retry_cap = session.retry_cap or 3

    environment = (
        session.environment
        or "dev.ges.store"
    )

    session.execution_status = "executing"
    session.execution_attempts = 0

    db.commit()

    # First execution
    run_result = executor.execute_spec(
        test_name,
        environment=environment
    )

    session.execution_attempts = 1

    session.execution_errors = (
        run_result.get("errors", "")
    )

    session.execution_time_ms = (
        run_result.get("duration_ms", 0)
    )

    if run_result["success"]:

        # Generate report
        report_path = reporter.generate_report(
            test_name,
            {
                **run_result,
                "healing_attempted": False
            },
            environment=environment,
            data_mode=session.data_mode
            or "inline"
        )

        session.execution_status = "passed"
        session.report_path = report_path
        session.report_csv_path = (
            report_path.replace(
                ".html",
                ".csv"
            )
        )

        db.commit()

        return {
            "status": "passed",
            "details": run_result["stdout"],
            "report_path": report_path,
            "execution_time_ms": run_result[
                "duration_ms"
            ],
            "healing_diffs": []
        }

    # Execution failed → attempt healing
    healing_summary = healer.attempt_heal(
        test_name,
        run_result,
        db,
        retry_cap=retry_cap,
        session_id=session_id
    )

    healing_diff_logs = (
        healing_summary.get(
            "healing_diffs",
            []
        )
    )

    if healing_summary.get("status") in (
        "application_defect",
        "environment_issue"
    ):

        # Not a healable issue — generate report
        report_path = reporter.generate_report(
            test_name,
            {
                **run_result,
                "healing_attempted": True,
                "healing_success": False
            },
            environment=environment,
            data_mode=session.data_mode
            or "inline",
            healing_diffs=healing_diff_logs
        )

        session.execution_status = (
            healing_summary["status"]
        )

        session.report_path = report_path

        session.report_csv_path = (
            report_path.replace(
                ".html",
                ".csv"
            )
        )

        session.healing_diffs = (
            json.dumps(
                healing_diff_logs
            )
        )

        db.commit()

        return {
            "status": healing_summary["status"],
            "message": healing_summary["message"],
            "healing_diffs": healing_diff_logs,
            "report_path": report_path
        }

    if healing_summary.get("healing_success"):

        # Healed — re-execute
        for attempt in range(
            2,
            retry_cap + 1
        ):

            retry_result = (
                executor.execute_spec(
                    test_name,
                    environment=environment,
                    retry_count_env=attempt - 1
                )
            )

            session.execution_attempts = attempt

            session.execution_time_ms = (
                retry_result.get(
                    "duration_ms",
                    0
                )
            )

            if retry_result["success"]:

                report_path = (
                    reporter.generate_report(
                        test_name,
                        {
                            **retry_result,
                            "healing_attempted": True,
                            "healing_success": True,
                            "retry_count": attempt - 1
                        },
                        environment=environment,
                        data_mode=session.data_mode
                        or "inline",
                        healing_diffs=healing_diff_logs
                    )
                )

                session.execution_status = "healed"

                session.report_path = report_path

                session.report_csv_path = (
                    report_path.replace(
                        ".html",
                        ".csv"
                    )
                )

                session.healing_diffs = (
                    json.dumps(
                        healing_diff_logs
                    )
                )

                db.commit()

                return {
                    "status": "healed_and_passed",
                    "message": (
                        f"Test healed and passed after "
                        f"{attempt} attempt(s)"
                    ),
                    "updated_code": (
                        healing_summary.get(
                            "updated_code",
                            ""
                        )
                    ),
                    "healing_diffs": healing_diff_logs,
                    "report_path": report_path,
                    "total_attempts": attempt
                }

    # All attempts failed — mark for manual review
    report_path = reporter.generate_report(
        test_name,
        {
            **run_result,
            "healing_attempted": True,
            "healing_success": False,
            "retry_count": session.execution_attempts
        },
        environment=environment,
        data_mode=session.data_mode
        or "inline",
        healing_diffs=healing_diff_logs
    )

    session.execution_status = (
        "failed_needs_review"
    )

    session.report_path = report_path

    session.report_csv_path = (
        report_path.replace(
            ".html",
            ".csv"
        )
    )

    session.healing_diffs = (
        json.dumps(
            healing_diff_logs
        )
    )

    db.commit()

    return {
        "status": "failed_needs_review",
        "message": (
            f"Test failed after "
            f"{session.execution_attempts} attempt(s). "
            f"Needs manual review."
        ),
        "healing_diffs": healing_diff_logs,
        "report_path": report_path,
        "final_errors": run_result.get(
            "errors",
            ""
        )
    }


@app.post("/workflow/dom-inspect")
def inspect_dom(
    environment: str = Form("dev.ges.store"),
    db: Session = Depends(get_db)
):
    """Inspect DOM of a target environment and return structured element data."""

    base_url = resolve_url(environment)

    dom_data = dom_inspector.extract_dom(
        base_url
    )

    return dom_data


@app.get("/workflow/session/{session_id}")
def get_session_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get the current status of a workflow session."""

    session = (
        db.query(WorkflowSession)
        .filter(
            WorkflowSession.session_id == session_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return {
        "session_id": session.session_id,
        "input_type": session.input_type,
        "environment": session.environment,
        "data_mode": session.data_mode,
        "user_confirmed": session.user_confirmed,
        "execution_status": session.execution_status,
        "execution_attempts": session.execution_attempts,
        "has_report": session.report_path is not None,
        "report_path": session.report_path,
        "report_csv_path": session.report_csv_path,
        "created_at": (
            session.created_at.isoformat()
            if session.created_at
            else None
        ),
        "updated_at": (
            session.updated_at.isoformat()
            if session.updated_at
            else None
        )
    }


@app.get("/workflow/download/{session_id}/{file_type}")
def download_file(
    session_id: str,
    file_type: str,
    db: Session = Depends(get_db)
):
    """Download generated files: script, page_object, report, csv_report."""

    session = (
        db.query(WorkflowSession)
        .filter(
            WorkflowSession.session_id == session_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    test_name = f"test_{session_id}"

    if file_type == "script":

        test_path = os.path.join(
            scaffolder.tests_dir,
            f"{test_name}.spec.js"
        )

        if os.path.exists(test_path):
            return FileResponse(
                test_path,
                filename=f"{test_name}.spec.js"
            )

    elif file_type == "page_object":

        page_path = os.path.join(
            scaffolder.pages_dir,
            f"{test_name}_page.page.js"
        )

        if os.path.exists(page_path):
            return FileResponse(
                page_path,
                filename=f"{test_name}_page.page.js"
            )

    elif file_type == "report":

        if (
            session.report_path
            and os.path.exists(
                session.report_path
            )
        ):
            return FileResponse(
                session.report_path,
                filename=f"report_{test_name}.html"
            )

    elif file_type == "csv_report":

        if (
            session.report_csv_path
            and os.path.exists(
                session.report_csv_path
            )
        ):
            return FileResponse(
                session.report_csv_path,
                filename=f"report_{test_name}.csv"
            )

    raise HTTPException(
        status_code=404,
        detail=(
            f"{file_type} not found "
            f"for session {session_id}"
        )
    )


@app.post("/workflow/download-all")
def download_all_files(
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Download all generated files as a zip archive."""

    import zipfile

    session = (
        db.query(WorkflowSession)
        .filter(
            WorkflowSession.session_id == session_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    test_name = f"test_{session_id}"

    temp_zip = os.path.join(
        UPLOAD_DIR,
        f"{session_id}_all_files.zip"
    )

    with zipfile.ZipFile(
        temp_zip,
        "w"
    ) as zipf:

        # Add test script
        test_path = os.path.join(
            scaffolder.tests_dir,
            f"{test_name}.spec.js"
        )

        if os.path.exists(test_path):
            zipf.write(
                test_path,
                f"tests/{test_name}.spec.js"
            )

        # Add page object
        page_path = os.path.join(
            scaffolder.pages_dir,
            f"{test_name}_page.page.js"
        )

        if os.path.exists(page_path):
            zipf.write(
                page_path,
                f"pages/{test_name}_page.page.js"
            )

        # Add HTML report
        if (
            session.report_path
            and os.path.exists(
                session.report_path
            )
        ):
            zipf.write(
                session.report_path,
                f"reports/report_{test_name}.html"
            )

        # Add CSV report
        if (
            session.report_csv_path
            and os.path.exists(
                session.report_csv_path
            )
        ):
            zipf.write(
                session.report_csv_path,
                f"reports/report_{test_name}.csv"
            )

        # Add test cases JSON
        if session.manual_test_cases:

            tc_path = os.path.join(
                UPLOAD_DIR,
                f"{session_id}_test_cases.json"
            )

            with open(
                tc_path,
                "w"
            ) as f:
                f.write(
                    session.manual_test_cases
                )

            zipf.write(
                tc_path,
                "test_cases.json"
            )

            os.remove(tc_path)

    return FileResponse(
        temp_zip,
        filename=f"{test_name}_all_files.zip",
        media_type="application/zip"
    )


@app.get("/workspace/pages")
def list_page_objects():
    """List all existing Page Objects in the repository."""

    return {
        "page_objects": pom_repo.list_page_objects()
    }


@app.get("/workspace/tests")
def list_tests():
    """List all generated test specs."""

    tests_dir = scaffolder.tests_dir

    tests = []

    if os.path.exists(tests_dir):

        for f in sorted(
            os.listdir(tests_dir)
        ):

            if f.endswith(".spec.js"):

                fpath = os.path.join(
                    tests_dir,
                    f
                )

                tests.append({
                    "name": f.replace(
                        ".spec.js",
                        ""
                    ),
                    "filename": f,
                    "size": os.path.getsize(
                        fpath
                    ),
                    "modified": (
                        datetime.datetime
                        .fromtimestamp(
                            os.path.getmtime(
                                fpath
                            )
                        )
                        .isoformat()
                    )
                })

    return {
        "tests": tests
    }


@app.get("/analytics/history")
def get_healing_history(
    db: Session = Depends(get_db)
):
    """Get all healing records."""

    return db.query(
        HealingRecord
    ).all()


@app.get("/analytics/auto-fix-diffs")
def get_auto_fix_diffs(
    session_id: str = None,
    db: Session = Depends(get_db)
):
    """Get auto-fix diff logs, optionally filtered by session."""

    query = db.query(
        AutoFixDiffLog
    )

    if session_id:
        query = query.filter(
            AutoFixDiffLog.session_id
            == session_id
        )

    return query.order_by(
        AutoFixDiffLog.timestamp.desc()
    ).all()


@app.get('/health')
def health():
    return {
        "model": "Gemini AI",
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    }