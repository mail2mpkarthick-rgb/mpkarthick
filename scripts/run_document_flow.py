import sys
import time

import requests

BASE = "http://127.0.0.1:8077"
DOC = r"D:\g_automation_ai\uploads\steps_for_function_testing.docx"


def main():
    t = time.time()
    with open(DOC, "rb") as f:
        r = requests.post(
            f"{BASE}/workflow/from-document",
            files={
                "file": (
                    "steps_for_function_testing.docx",
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={
                "environment": "dev",
                "data_mode": "inline",
                "retry_cap": 3,
                "dom_inspection": "false",
                "browser_mode": "headless",
            },
            timeout=600,
        )
    el = round(time.time() - t, 1)
    print(f"status={r.status_code} elapsed={el}s")
    if r.status_code != 200:
        print(r.text[:1200])
        sys.exit(1)

    j = r.json()
    print("session_id:", j["session_id"])
    for tc in j["manual_test_cases"]:
        print(f"\n[{tc['id']}] {tc['title']}")
        print("  desc:", tc.get("description", "")[:160])
        for s in tc.get("steps", []):
            print("   -", s[:150])
        print("  expected:", tc.get("expected", "")[:200])


if __name__ == "__main__":
    main()
