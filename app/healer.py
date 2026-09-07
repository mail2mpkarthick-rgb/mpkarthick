import os
import json
import difflib
from app.agent import GeminiAgent
from app.generator import CodeScaffolder
from app.database import AutoFixDiffLog
from app.logging_conf import get_logger
from sqlalchemy.orm import Session

log = get_logger(__name__)


class SelfHealer:
    """Guardrailed auto-healing with failure classification, multi-strategy fallback, and diff logging."""

    # Multi-strategy locator fallback patterns
    FALLBACK_STRATEGIES = [
        "text",           # page.getByText('Button Text')
        "role",           # page.getByRole('button', { name: '...' })
        "css",            # page.locator('css-selector')
        "aria-label",     # page.getByLabel('Label text')
        "placeholder",    # page.getByPlaceholder('Placeholder')
        "testid",         # page.getByTestId('data-testid-value')
        "xpath",          # page.locator('//xpath')
        "nth-child",      # page.locator('parent-selector').nth(N)
    ]

    def __init__(self, agent: GeminiAgent, scaffolder: CodeScaffolder):
        self.agent = agent
        self.scaffolder = scaffolder

    def attempt_heal(self, test_name: str, execution_result: dict, db: Session, 
                     retry_cap: int = 3,
                     session_id: str = None) -> dict:
        """
        Attempt to heal a failing test with guardrailed auto-fix.
        
        1. Classify the failure (script_issue vs application_defect vs environment_issue)
        2. Only auto-fix script_issue failures
        3. Apply multi-strategy locator fallback
        4. Cap retry attempts
        5. Log all changes as before/after diffs
        """
        original_code = self.scaffolder.read_test(test_name)
        if not original_code:
            return {"status": "error", "message": f"Test {test_name} not found", "healing_success": False}

        error_log = execution_result.get("stderr") or execution_result.get("stdout") or ""
        screenshot = execution_result.get("screenshot_path")
        
        # Step 1: Classify the failure
        failure_type = self.agent.classify_failure(error_log, original_code)
        
        healing_diffs = []
        
        # Step 2: Only auto-fix script issues
        if failure_type == "application_defect":
            self._log_diff(db, session_id or "", test_name, 0, failure_type, 
                          error_log, original_code, original_code, 
                          "APPLICATION DEFECT detected - auto-fix skipped. Flagged for manual review.", False)
            return {
                "status": "application_defect",
                "message": "Application defect detected. Auto-fix skipped — needs manual review.",
                "healing_success": False,
                "failure_type": failure_type,
                "healing_diffs": [{"attempt_number": 0, "failure_type": failure_type, 
                                   "success": False, "diff_summary": "Application defect — auto-fix not allowed"}]
            }
        
        if failure_type == "environment_issue":
            self._log_diff(db, session_id or "", test_name, 0, failure_type,
                          error_log, original_code, original_code,
                          "ENVIRONMENT/DATA issue detected - auto-fix skipped. User remediation needed.", False)
            return {
                "status": "environment_issue",
                "message": "Environment or data issue detected. Auto-fix skipped — please check target environment and test data.",
                "healing_success": False,
                "failure_type": failure_type,
                "healing_diffs": [{"attempt_number": 0, "failure_type": failure_type,
                                   "success": False, "diff_summary": "Environment/data issue — auto-fix not allowed"}]
            }
        
        # Step 3: Script issue — attempt multi-strategy healing with retry cap
        current_code = original_code
        attempt = 0
        max_attempts = min(retry_cap, 3)  # Hard cap at 3
        
        while attempt < max_attempts:
            attempt += 1
            strategy_index = min(attempt - 1, len(self.FALLBACK_STRATEGIES) - 1)
            current_strategy = self.FALLBACK_STRATEGIES[strategy_index]
            
            try:
                # Generate fix using the agent with current strategy context
                strategy_prompt = f"""
                The current selector strategy '{current_strategy}' is failing. 
                Try alternative selectors using these strategies in order:
                1. Try different attribute (role, aria-label, data-testid, placeholder, name)
                2. Try CSS selector based on nearby elements
                3. Try XPath relative positioning
                4. Try getByText with partial match
                
                Current failing strategy: {current_strategy}
                """
                
                healed_code = self.agent.generate_fix(
                    current_code, 
                    error_log + f"\n\nHealing attempt #{attempt} - Strategy: {current_strategy}\n{strategy_prompt}",
                    screenshot_path=screenshot,
                    failure_type=failure_type
                )
                
                if not healed_code or healed_code == current_code:
                    continue
                
                # Apply the fix
                self.scaffolder.save_test(test_name, healed_code)
                
                # Calculate diff
                diff_lines = list(difflib.unified_diff(
                    current_code.splitlines(keepends=True),
                    healed_code.splitlines(keepends=True),
                    fromfile='original',
                    tofile='healed',
                    n=3
                ))
                diff_summary = ''.join(diff_lines[:30])  # Limit diff output
                
                # Log this fix attempt
                self._log_diff(db, session_id or "", test_name, attempt, failure_type,
                              error_log, current_code, healed_code, diff_summary, True)
                
                healing_diffs.append({
                    "attempt_number": attempt,
                    "failure_type": failure_type,
                    "strategy": current_strategy,
                    "success": True,
                    "diff_summary": diff_summary[:500]
                })
                
                current_code = healed_code
                
            except Exception as e:
                diff_summary = f"Error during healing attempt {attempt}: {str(e)}"
                healing_diffs.append({
                    "attempt_number": attempt,
                    "failure_type": failure_type,
                    "strategy": current_strategy,
                    "success": False,
                    "diff_summary": diff_summary
                })
        
        # Step 4: If all attempts exhausted, mark for manual review
        if not healing_diffs or not any(d.get("success") for d in healing_diffs):
            # Restore original code
            self.scaffolder.save_test(test_name, original_code)
            return {
                "status": "healing_failed",
                "message": f"Auto-healing failed after {attempt} attempts. Test marked for manual review.",
                "healing_success": False,
                "failure_type": failure_type,
                "healing_diffs": healing_diffs
            }
        
        return {
            "status": "healed",
            "updated_code": current_code,
            "healing_success": True,
            "failure_type": failure_type,
            "attempts": attempt,
            "healing_diffs": healing_diffs
        }

    def _log_diff(self, db: Session, session_id: str, test_name: str,
                  attempt_number: int, failure_type: str, error_log: str,
                  original_code: str, healed_code: str, diff_summary: str,
                  success: bool):
        """Persist a healing diff record to the database."""
        try:
            record = AutoFixDiffLog(
                session_id=session_id,
                test_name=test_name,
                attempt_number=attempt_number,
                failure_type=failure_type,
                error_log=error_log[:1000],
                original_code=original_code,
                healed_code=healed_code,
                diff_summary=diff_summary[:1000],
                success=success
            )
            db.add(record)
            db.commit()
        except Exception:
            log.exception(
                "Failed to persist healing diff (session=%s test=%s attempt=%s)",
                session_id, test_name, attempt_number,
            )
            db.rollback()

