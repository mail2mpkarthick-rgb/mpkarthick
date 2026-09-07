import time

import requests

BASE = "http://127.0.0.1:8077"
PROMPT = (
    "Test the login page with valid and invalid username and password. "
    "Verify that the user can log in successfully with valid credentials "
    "and an error message is displayed for invalid credentials."
)


def run(n=4):
    ok = 0
    for i in range(n):
        t = time.time()
        r = requests.post(
            f"{BASE}/workflow/from-prompt",
            data={
                "prompt": PROMPT,
                "environment": "dev",
                "data_mode": "inline",
                "retry_cap": 3,
                "dom_inspection": "false",
                "browser_mode": "headless",
            },
            timeout=400,
        )
        el = round(time.time() - t, 1)
        if r.status_code == 200:
            ok += 1
            titles = [x["title"] for x in r.json()["manual_test_cases"]]
            print(f"run{i+1} {el}s OK -> {titles[:3]}")
        else:
            print(f"run{i+1} {el}s {r.status_code} -> {r.text[:250]}")
    print(f"--- {ok}/{n} succeeded ---")


if __name__ == "__main__":
    run()
