import os
import json
import csv
import datetime


class ReportGenerator:
    def __init__(self, reports_dir: str = "./workspace/reports"):
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)

    def generate_report(self, test_name: str, execution_data: dict,
                        environment: str = "dev.ges.store",
                        data_mode: str = "inline",
                        healing_diffs: list = None) -> str:
        """Creates an enhanced HTML report for a completed test workflow."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        passed = execution_data.get("success", False)
        duration = execution_data.get("duration_ms", 0)
        errors = execution_data.get("errors", "")
        stdout_log = execution_data.get("stdout", "")
        healing_attempted = execution_data.get("healing_attempted", False)
        healing_success = execution_data.get("healing_success", False)
        total_steps = execution_data.get("total_steps", 0)
        passed_steps = execution_data.get("passed_steps", 0)
        failed_steps = execution_data.get("failed_steps", 0)
        retry_count = execution_data.get("retry_count", 0)
        screenshot_path = execution_data.get("screenshot_path", None)

        status_badge = '<span style="color:#28a745;font-weight:700">PASSED &#10004;</span>' if passed else '<span style="color:#dc3545;font-weight:700">FAILED &#10008;</span>'

        # Healing info
        healing_info = ""
        if healing_attempted:
            if healing_success:
                healing_info = '<p style="color:#28a745;">&#9889; Self-healing applied successfully</p>'
            else:
                healing_info = '<p style="color:#dc3545;">&#9889; Self-healing attempted but failed — needs manual review</p>'

        # Auto-fix diff log section
        diff_section = ""
        if healing_diffs:
            diff_entries = ""
            for i, diff in enumerate(healing_diffs):
                attempt_num = diff.get("attempt_number", i + 1)
                failure_type = diff.get("failure_type", "script_issue")
                diff_summary = diff.get("diff_summary", "No summary available")
                diff_success = diff.get("success", False)
                status_icon = "&#10004;" if diff_success else "&#10008;"
                diff_entries += f"""
                <div style="background:#f8f9fa;border:1px solid #dee2e6;border-radius:6px;padding:12px;margin-bottom:8px">
                    <p><strong>Attempt #{attempt_num}</strong> - Type: <code>{failure_type}</code> - {status_icon}</p>
                    <pre style="background:#fff;padding:8px;border-radius:4px;font-size:0.82em;overflow-x:auto">{diff_summary}</pre>
                </div>"""
            
            diff_section = f"""
            <div class="details">
                <h3>&#9889; Auto-Fix Diff Log ({len(healing_diffs)} attempt(s))</h3>
                {diff_entries}
            </div>"""

        # Screenshot section
        screenshot_section = ""
        if screenshot_path and os.path.exists(screenshot_path):
            screenshot_section = f"""
            <div class="details">
                <h3>Failure Screenshot</h3>
                <img src="../../{screenshot_path}" alt="Failure screenshot" style="max-width:100%;border:1px solid #dee2e6;border-radius:6px;" />
            </div>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Test Report - {test_name}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#1a1a2e;padding:20px}}
.container{{max-width:900px;margin:0 auto}}
.header{{background:linear-gradient(135deg,#1a1a2e,#16213e);color:#eee;border-radius:12px;padding:24px;margin-bottom:20px}}
.header h1{{font-size:1.4em;margin-bottom:4px}}
.header .meta{{font-size:0.85em;color:#a8d8ea;margin-top:8px}}
.badge{{font-size:1.2em;margin:10px 0}}
.env-info{{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px}}
.env-tag{{background:rgba(255,255,255,0.1);padding:4px 10px;border-radius:12px;font-size:0.8em}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin-bottom:20px}}
.stat-card{{background:#fff;border-radius:10px;padding:16px;border:1px solid #e0e0e0;text-align:center}}
.stat-card .num{{font-size:1.6em;font-weight:700;color:#1a1a2e}}
.stat-card .label{{font-size:0.8em;color:#666;margin-top:4px}}
.details{{background:#fff;border-radius:10px;padding:20px;border:1px solid #e0e0e0;margin-bottom:20px}}
.details h3{{font-size:1em;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #eee}}
.details pre{{background:#f5f5f5;padding:12px;border-radius:6px;font-size:0.85em;overflow-x:auto;white-space:pre-wrap;word-break:break-all}}
.details .output{{background:#1a1a2e;color:#a8d8ea;padding:12px;border-radius:6px;font-size:0.85em;overflow-x:auto;white-space:pre-wrap;word-break:break-all}}
.footer{{text-align:center;font-size:0.8em;color:#999;padding:16px 0}}
.btn{{display:inline-block;padding:8px 16px;background:#007bff;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85em;margin:4px}}
.btn:hover{{background:#0056b3}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>Test Execution Report</h1>
<p style="font-size:0.9em">{test_name}</p>
<div class="meta">Executed: {timestamp} | Environment: <strong>{environment}</strong> | Data Mode: <strong>{data_mode}</strong></div>
<div class="badge">{status_badge}</div>
{healing_info}
</div>
<div class="stats">
<div class="stat-card"><div class="num">{duration}ms</div><div class="label">Duration</div></div>
<div class="stat-card"><div class="num">{total_steps}</div><div class="label">Total Steps</div></div>
<div class="stat-card"><div class="num" style="color:#28a745">{passed_steps}</div><div class="label">Passed</div></div>
<div class="stat-card"><div class="num" style="color:#dc3545">{failed_steps}</div><div class="label">Failed</div></div>
<div class="stat-card"><div class="num">{retry_count}</div><div class="label">Retries</div></div>
</div>
{diff_section}
{screenshot_section}
<div class="details">
<h3>Execution Output</h3>
<div class="output">{(errors if errors else stdout_log if stdout_log else "No output captured.")}</div>
</div>
<div class="details">
<h3>Download Options</h3>
<p><a href="../../workspace/reports/report_{test_name.replace('.spec.js','').replace('.','_')}.csv" class="btn" download>Download CSV Report</a></p>
</div>
<div class="footer">Generated by G_Automation_AI v2 | &#169; 2024</div>
</body>
</html>"""

        safe_name = test_name.replace(".spec.js", "").replace(".", "_")
        filename = f"report_{safe_name}.html"
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        # Also generate CSV report
        self.generate_csv_report(test_name, execution_data, environment, data_mode, healing_diffs)

        return filepath

    def generate_csv_report(self, test_name: str, execution_data: dict,
                            environment: str = "dev.ges.store",
                            data_mode: str = "inline",
                            healing_diffs: list = None) -> str:
        """Generates a CSV export of the test report."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        passed = execution_data.get("success", False)
        duration = execution_data.get("duration_ms", 0)
        errors = execution_data.get("errors", "")
        total_steps = execution_data.get("total_steps", 0)
        passed_steps = execution_data.get("passed_steps", 0)
        failed_steps = execution_data.get("failed_steps", 0)
        retry_count = execution_data.get("retry_count", 0)

        safe_name = test_name.replace(".spec.js", "").replace(".", "_")
        filepath = os.path.join(self.reports_dir, f"report_{safe_name}.csv")

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Test Report", test_name])
            writer.writerow(["Timestamp", timestamp])
            writer.writerow(["Environment", environment])
            writer.writerow(["Data Mode", data_mode])
            writer.writerow(["Status", "PASSED" if passed else "FAILED"])
            writer.writerow(["Duration (ms)", duration])
            writer.writerow(["Total Steps", total_steps])
            writer.writerow(["Passed Steps", passed_steps])
            writer.writerow(["Failed Steps", failed_steps])
            writer.writerow(["Retry Count", retry_count])
            writer.writerow([])
            writer.writerow(["Error Details"])
            writer.writerow([errors])
            
            if healing_diffs:
                writer.writerow([])
                writer.writerow(["Auto-Fix Diff Log"])
                writer.writerow(["Attempt", "Failure Type", "Success", "Summary"])
                for i, diff in enumerate(healing_diffs):
                    attempt_num = diff.get("attempt_number", i + 1)
                    failure_type = diff.get("failure_type", "script_issue")
                    diff_success = diff.get("success", False)
                    diff_summary = diff.get("diff_summary", "")
                    writer.writerow([attempt_num, failure_type, diff_success, diff_summary])

        return filepath

