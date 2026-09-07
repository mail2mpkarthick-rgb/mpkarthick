import subprocess
import os
import time
import json


class TestExecutor:
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = workspace_path

    def execute_spec(self, test_name: str, 
                     environment: str = "dev.ges.store",
                     retry_count_env: int = 0,
                     headless: bool = True) -> dict:
        """Triggers Playwright execution with environment-specific settings.

        Args:
            test_name: Name of the test spec file
            environment: Target environment URL or env name
            retry_count_env: Number of retries for this execution
            headless: Whether to run browser in headless mode (default: True)
        """
        filename = f"{test_name}.spec.js" if not test_name.endswith(".spec.js") else test_name
        # Resolve environment: "dev" -> "dev.ges.store", "uat" -> "uat.ges.store"
        env_map = {"dev": "dev.ges.store", "uat": "uat.ges.store"}
        resolved_env = env_map.get(environment, environment)
        base_url = f"https://{resolved_env}" if not resolved_env.startswith("http") else resolved_env

        start_time = time.time()
        try:
            # Set environment variables for Playwright config
            env = os.environ.copy()
            env["BASE_URL"] = base_url
            env["RETRY_COUNT"] = str(retry_count_env)
            env["HEADLESS"] = str(headless).lower()

            # Cross-platform npx command
            npx_cmd = "npx"  # Use 'npx' directly - works cross-platform
            cmd = [
                npx_cmd,
                "playwright",
                "test",
                f"tests/{filename}",
                "--reporter=json",
                "--reporter=html",
                "--reporter=line"
            ]
            result = subprocess.run(
                cmd,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                shell=False,
                env=env
            )
            elapsed_ms = int((time.time() - start_time) * 1000)
            success = result.returncode == 0

            # Try to parse Playwright JSON results
            passed_steps = 0
            failed_steps = 0
            total_steps = 0
            results_parse_error = None
            try:
                results_path = os.path.join(self.workspace_path, "reports", "test-results.json")
                if os.path.exists(results_path):
                    with open(results_path, "r") as f:
                        pw_results = json.load(f)
                    if isinstance(pw_results, list):
                        for suite in pw_results:
                            for spec in suite.get("specs", []):
                                total_steps += 1
                                tests = spec.get("tests", [])
                                for t in tests:
                                    status = t.get("status", "unknown")
                                    if status == "passed":
                                        passed_steps += 1
                                    else:
                                        failed_steps += 1
            except (json.JSONDecodeError, FileNotFoundError) as e:
                # Counts stay 0 and are reported as unknown; never fabricate pass/fail.
                results_parse_error = str(e)

            # Find failure screenshot if any
            failure_screenshot = None
            if not success:
                screenshot_dir = os.path.join(self.workspace_path, "test-results", test_name)
                if os.path.exists(screenshot_dir):
                    for file in os.listdir(screenshot_dir):
                        if file.endswith(".png"):
                            failure_screenshot = os.path.join(screenshot_dir, file)
                            break

            errors = result.stderr or result.stdout
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_ms": elapsed_ms,
                "errors": errors,
                "screenshot_path": failure_screenshot,
                "total_steps": total_steps,
                "passed_steps": passed_steps,
                "failed_steps": failed_steps,
                "results_parse_error": results_parse_error,
                "retry_count": retry_count_env
            }

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "stdout": "",
                "stderr": f"System execution engine failed to spawn process: {str(e)}",
                "duration_ms": elapsed_ms,
                "errors": str(e),
                "screenshot_path": None,
                "total_steps": 1,
                "passed_steps": 0,
                "failed_steps": 1,
                "retry_count": retry_count_env
            }

