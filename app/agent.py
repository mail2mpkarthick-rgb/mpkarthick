import os
import json
import re
import time
import mimetypes

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.logging_conf import get_logger

load_dotenv()

log = get_logger(__name__)


def _retry_delay_from_error(err_text: str):
    """Honour the server's retryDelay hint (e.g. 'retryDelay': '11s') when present."""
    m = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+(?:\.\d+)?)s", err_text)
    if m:
        return min(float(m.group(1)) + 1.0, 60.0)
    return None



class GeminiAgent:
    def __init__(
        self,
        test_gen_model: str = "gemini-3.6-flash",
        code_gen_model: str = "gemini-3.6-flash",
        vision_model: str = "gemini-3.6-flash",
        keep_alive: str = "30m",
        timeout: int = 120,
        max_retries: int = 4,
        retry_base_delay: float = 2.0,
    ):
        self.test_gen_model = test_gen_model
        self.code_gen_model = code_gen_model
        self.vision_model = vision_model
        self.keep_alive = keep_alive
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay

        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file"
            )

        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=self.timeout * 1000),
        )

    def _generate(self, model, prompt=None, images=None, **kwargs):
        """Wrapper around Gemini API with text and image support."""

        contents = []

        if prompt:
            contents.append(prompt)

        if images:
            for image_path in images:
                if not image_path or not os.path.exists(image_path):
                    continue

                try:
                    with open(image_path, "rb") as image_file:
                        image_bytes = image_file.read()

                    mime_type, _ = mimetypes.guess_type(image_path)

                    if not mime_type:
                        mime_type = "image/png"

                    contents.append(
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=mime_type,
                        )
                    )

                except Exception as e:
                    print(
                        f"Warning: Could not load image '{image_path}': {e}"
                    )

        config_kwargs = {}

        if "temperature" in kwargs:
            config_kwargs["temperature"] = kwargs["temperature"]

        if "max_output_tokens" in kwargs:
            config_kwargs["max_output_tokens"] = kwargs[
                "max_output_tokens"
            ]

        config = None

        if config_kwargs:
            config = types.GenerateContentConfig(
                **config_kwargs
            )

        last_error = None

        for attempt in range(self.max_retries):
            try:
                if config:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config,
                    )
                else:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contents,
                    )

                return {
                    "response": response.text or ""
                }

            except Exception as e:
                last_error = e
                err_text = str(e)
                daily_cap = "PerDay" in err_text or "per_day" in err_text
                transient = any(
                    code in err_text
                    for code in ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED")
                )

                # A daily quota cap will not clear within a request; fail fast.
                if daily_cap or not transient or attempt == self.max_retries - 1:
                    break

                delay = _retry_delay_from_error(err_text)
                if delay is None:
                    delay = self.retry_base_delay * (2 ** attempt)

                log.warning(
                    "Gemini transient error (attempt %d/%d), retrying in %.1fs: %.200s",
                    attempt + 1, self.max_retries, delay, str(e),
                )
                time.sleep(delay)

        raise RuntimeError(
            f"Gemini API generation failed after {self.max_retries} attempt(s): {last_error}"
        ) from last_error

    def _get_model_for_task(self, task: str = "test_generation"):
        """Select the appropriate Gemini model based on task type."""

        if task == "test_generation":
            return self.test_gen_model

        elif task in ("code_generation", "auto_fix"):
            return self.code_gen_model

        elif task == "vision":
            return self.vision_model

        return self.code_gen_model

    def generate_manual_tests(
        self,
        input_text: str,
        input_type: str = "prompt",
        environment: str = "dev.ges.store",
        dom_context: str = None,
        image_context: str = None,
    ) -> str:
        """Generate manual test cases from prompt, document, or multimodal input."""

        type_label = (
            "user prompt"
            if input_type == "prompt"
            else "uploaded document"
        )

        dom_section = ""

        if dom_context:
            dom_section = (
                "\n\nLIVE DOM / LOCATOR CONTEXT "
                "(real page structure):\n"
                f"{dom_context}"
            )

        image_section = ""

        if image_context:
            image_section = (
                "\n\nSCREENSHOT / IMAGE ANALYSIS "
                "(user-attached visual context):\n"
                f"{image_context}"
            )

        prompt = f"""
        You are a QA engineer. Based on the following {type_label}, generate manual test cases for the target environment: {environment}.

        {input_text}
        {dom_section}
        {image_section}

        CRITICAL RULES:
        1. Output ONLY a JSON array of test case objects. NO markdown, NO explanations, NO extra text.
        2. Format each object as: {{"id": "TC_1", "title": "Short test title", "description": "What to test", "steps": ["Step 1...", "Step 2..."], "expected": "Expected result"}}
        3. Cover both POSITIVE and NEGATIVE scenarios. Include edge cases.
        4. Minimum 3 test cases, maximum 8.
        5. Output MUST start with '[' and end with ']'. Valid JSON only.
        6. If DOM context is provided, use real element names/selectors in your steps. If not, use descriptive UI labels.
        """

        model = self._get_model_for_task(
            "test_generation"
        )

        response = self._generate(
            model=model,
            prompt=prompt,
        )

        return self._clean_json_output(
            response["response"].strip()
        )

    def generate_pom_scripts(
        self,
        manual_tests_json: str,
        environment: str = "dev.ges.store",
        dom_context: str = None,
        existing_pom_code: str = None,
        data_mode: str = "inline",
        data_source_path: str = None,
    ) -> dict:
        """Generate Playwright POM scripts with DOM grounding and POM repository reuse."""

        base_url = (
            f"https://{environment}"
            if not environment.startswith("http")
            else environment
        )

        dom_section = ""

        if dom_context:
            dom_section = (
                "\n\nLIVE DOM STRUCTURE "
                "(use these real selectors):\n"
                f"{dom_context}"
            )

        existing_section = ""

        if existing_pom_code:
            existing_section = (
                "\n\nEXISTING PAGE OBJECTS "
                "(reuse/extend these):\n"
                f"{existing_pom_code}"
            )

        data_section = ""

        if data_mode == "data-driven" and data_source_path:
            data_section = (
                "\n\nDATA-DRIVEN MODE: The test should read "
                f"input data from '{data_source_path}' "
                "and write Pass/Fail results back."
            )

        prompt = f"""
        You are a test automation engineer. Convert these manual test cases into Playwright JavaScript using the Page Object Model (POM) pattern.

        Target environment base URL: {base_url}

        {dom_section}
        {existing_section}
        {data_section}

        MANUAL TEST CASES:
        {manual_tests_json}

        CRITICAL RULES:
        1. Generate TWO separate code blocks: PAGE CLASS and TEST FILE.
        2. PAGE CLASS: A reusable Page Object class with locators and methods for each action.
        3. TEST FILE: A spec file that imports the Page class and runs the test cases.
        4. Use `const {{ test, expect }} = require('@playwright/test');` syntax.
        5. Use EXACT selectors from the DOM context if provided; otherwise use robust selectors (button text, role, aria labels, data-testid, CSS classes).
        6. Output format:
           ---PAGE---
           [page class code here]
           ---TEST---
           [test spec code here]
        7. NO explanations, NO markdown backticks, NO extra text. ONLY the code blocks separated by ---PAGE--- and ---TEST---.
        8. For data-driven mode, the test should loop over rows from a data source.
        """

        model = self._get_model_for_task(
            "code_generation"
        )

        response = self._generate(
            model=model,
            prompt=prompt,
        )

        return self._parse_pom_output(
            response["response"].strip()
        )

    def _clean_json_output(self, text: str) -> str:
        """Extract valid JSON array from model output."""

        text = (
            text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        start = text.find("[")
        end = text.rfind("]")

        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]

        return text

    def _parse_pom_output(self, text: str) -> dict:
        """Parse ---PAGE--- and ---TEST--- sections from model output."""

        result = {
            "page_code": "",
            "test_code": "",
        }

        if "---PAGE---" in text and "---TEST---" in text:

            parts = text.split("---TEST---")

            page_section = parts[0]

            test_section = (
                parts[1]
                if len(parts) > 1
                else ""
            )

            if "---PAGE---" in page_section:
                result["page_code"] = (
                    page_section
                    .split("---PAGE---")[1]
                    .strip()
                )

            result["test_code"] = test_section.strip()

        else:
            result["test_code"] = self._clean_code_output(
                text
            )

        result["page_code"] = (
            result["page_code"]
            .replace("```javascript", "")
            .replace("```js", "")
            .replace("```", "")
            .strip()
        )

        result["test_code"] = (
            result["test_code"]
            .replace("```javascript", "")
            .replace("```js", "")
            .replace("```", "")
            .strip()
        )

        return result

    def analyze_image(self, image_path: str) -> dict:
        """Use Gemini vision capability to interpret a screenshot/image."""

        if not os.path.exists(image_path):
            return {
                "elements": [],
                "error": "Image file not found",
                "confidence": 0,
            }

        try:
            model = self._get_model_for_task(
                "vision"
            )

            prompt = """
            Describe in detail all visible UI elements in this screenshot.

            For each element, specify:
            - Type (button, input field, label, link, image, heading, etc.)
            - Text or label content
            - Approximate position (top, bottom, left, right, center)
            - Any visible state (disabled, error, selected, etc.)

            If you cannot identify specific elements, describe the general layout and any visible text.

            Output as JSON array:
            [{"type": "button", "label": "Submit", "position": "center-right", "state": "enabled"}]

            IMPORTANT:
            Output ONLY the JSON array.
            No markdown.
            No explanation.
            """

            response = self._generate(
                model=model,
                prompt=prompt,
                images=[image_path],
            )

            raw = response["response"].strip()

            elements = self._clean_json_output(
                raw
            )

            try:
                parsed = (
                    json.loads(elements)
                    if elements.startswith("[")
                    else []
                )

                return {
                    "elements": parsed,
                    "confidence": 0.7,
                    "error": None,
                }

            except json.JSONDecodeError:
                return {
                    "elements": [],
                    "raw_description": raw,
                    "confidence": 0.3,
                    "error": "Could not parse structured elements",
                }

        except Exception as e:
            return {
                "elements": [],
                "confidence": 0,
                "error": str(e),
            }

    def generate_csv_matrix(
        self,
        combined_instructions: str,
        screenshot_path: str = None,
        environment: str = "dev.ges.store",
    ) -> str:
        """Analyzes document text and screenshot to build CSV test matrix."""

        prompt = f"""
        Analyze this UI screenshot and the provided document requirements to build a comprehensive QA test case matrix in standard CSV format.

        Target environment: {environment}

        CRITICAL RULES:
        1. Look closely at the image. Identify the real buttons, input fields, and layout elements visible on the screen.
        2. Generate complete POSITIVE and NEGATIVE validation steps based on what is actually on this screen.
        3. Columns must be exactly: ID,Test Case Description,Execution Step,Expected Result
        4. Separate cells with a standard comma (,). Wrap any text containing commas in double quotes (").
        5. Output ONLY the raw CSV text rows. No explanations, no notes, no markdown code block backticks.

        CONTEXT DATA:
        {combined_instructions}
        """

        images = (
            [screenshot_path]
            if screenshot_path
            and os.path.exists(screenshot_path)
            else None
        )

        model = self._get_model_for_task(
            "test_generation"
        )

        response = self._generate(
            model=model,
            prompt=prompt,
            images=images,
        )

        return (
            response["response"]
            .strip()
            .replace("```csv", "")
            .replace("```", "")
        )

    def generate_script_from_csv(
        self,
        csv_matrix: str,
        environment: str = "dev.ges.store",
    ) -> str:
        """Converts CSV test matrix into Playwright JS."""

        prompt = f"""
        Convert the following structural CSV action scenarios into sequential automation steps using Playwright JavaScript.

        Target environment: {environment}

        CSV SCENARIO MATRIX:
        {csv_matrix}

        Coding Standards:
        1. Use exactly: const {{ test, expect }} = require('@playwright/test');
        2. Encapsulate all items sequentially inside a clean async/await test block wrapper.
        3. Target selectors based on real elements. Output raw runnable code only with NO markdown backticks or commentary.
        4. STRICT RULE: Output ONLY the raw JavaScript code. NO explanations, NO notes, NO introductory text, NO "Here is" phrases. NOTHING except the code.
        """

        model = self._get_model_for_task(
            "code_generation"
        )

        response = self._generate(
            model=model,
            prompt=prompt,
        )

        return self._clean_code_output(
            response["response"].strip()
        )

    def _clean_code_output(self, text: str) -> str:
        """Strips all non-code commentary from AI output, leaving only valid JavaScript."""

        text = (
            text
            .replace("```javascript", "")
            .replace("```js", "")
            .replace("```", "")
        )

        lines = text.strip().split("\n")

        cleaned_lines = []

        found_code = False

        for line in lines:

            stripped = line.strip()

            if not found_code:

                if (
                    stripped.startswith("const")
                    or stripped.startswith("import")
                    or stripped.startswith("test(")
                    or stripped.startswith("describe")
                ):

                    if stripped:
                        found_code = True
                        cleaned_lines.append(line)

                    continue

                elif stripped == "":
                    continue

                else:
                    continue

            else:

                if (
                    stripped.startswith("Note:")
                    or stripped.startswith("Note that")
                    or (
                        stripped.startswith("This")
                        and "correct" in stripped.lower()
                    )
                ):
                    break

                cleaned_lines.append(line)

        return "\n".join(
            cleaned_lines
        ).strip()

    def generate_fix(
        self,
        broken_code: str,
        error_log: str,
        screenshot_path: str = None,
        failure_type: str = "script_issue",
    ) -> str:
        """
        Analyzes a runtime failure snapshot to patch
        broken locator selectors.

        Only modifies locators, waits, and selector strategy
        — never assertions.
        """

        guardrails = ""

        if failure_type == "script_issue":

            guardrails = """
            ALLOWED CHANGES:
            - Update locator selectors (CSS, XPath, text, role, etc.)
            - Adjust wait/ timing strategies (timeout values, waitFor* calls)
            - Change selector strategy (e.g., text -> role -> data-testid fallback)

            FORBIDDEN CHANGES:
            - DO NOT modify test assertions (expect calls, assert statements)
            - DO NOT change expected outcomes or test logic
            - DO NOT add try/catch to mask failures
            """

        elif failure_type == "application_defect":

            guardrails = """
            WARNING: This failure appears to be an APPLICATION DEFECT, not a script issue.
            DO NOT auto-fix. Flag this as a potential bug.
            Only output the original code unchanged with a comment noting the potential defect.
            """

        elif failure_type == "environment_issue":

            guardrails = """
            WARNING: This failure appears to be an ENVIRONMENT or DATA issue.
            DO NOT auto-fix. Flag this for user remediation.
            Only output the original code unchanged with a comment noting the environment issue.
            """

        prompt = f"""
        An automation script crashed. Analyze the code, the error, and the failure snapshot to output a corrected version.

        BROKEN CODE:
        {broken_code}

        EXCEPTION:
        {error_log}

        {guardrails}

        CRITICAL RULES:
        1. Output ONLY the raw JavaScript code. No explanations, no notes, no introductory text.
        2. Use require syntax: const {{ test, expect }} = require('@playwright/test');
        3. NOTHING except the code.
        """

        images = (
            [screenshot_path]
            if screenshot_path
            and os.path.exists(screenshot_path)
            else None
        )

        model = self._get_model_for_task(
            "auto_fix"
        )

        response = self._generate(
            model=model,
            prompt=prompt,
            images=images,
        )

        return self._clean_code_output(
            response["response"].strip()
        )

    def classify_failure(
        self,
        error_log: str,
        test_code: str = "",
    ) -> str:
        """Classify an execution failure."""

        prompt = f"""
        Classify this test automation failure into exactly one category:

        FAILURE ERROR:
        {error_log[:2000]}

        TEST CODE:
        {test_code[:2000]}

        Categories:
        - "script_issue": Locator not found, timeout, wait failure, selector strategy problem, stale element
        - "application_defect": Button missing, flow broken, UI element behaves differently than expected, assertion failure on real behavior
        - "environment_issue": Target URL unreachable, network error, authentication failure, missing test data, server error (5xx), SSL error

        Respond with ONLY one word: script_issue, application_defect, or environment_issue.

        Do NOT include any explanations, markdown formatting, or extra text.
        """

        model = self._get_model_for_task(
            "test_generation"
        )

        response = self._generate(
            model=model,
            prompt=prompt,
        )

        classification = (
            response["response"]
            .strip()
            .lower()
        )

        if "application_defect" in classification:
            return "application_defect"

        elif "environment_issue" in classification:
            return "environment_issue"

        else:
            return "script_issue"