g_automation_ai/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI Application Gateway & Static UI Router
│   ├── database.py          # SQLite Context for Self-Healing Analytics Memory
│   ├── parser.py            # Extraction Engine (Tesseract OCR & Document Text)
│   ├── agent.py             # Ollama Multi-Modal LLM Core Orchestrator
│   ├── generator.py         # Playwright POM Boilerplate Code Scaffolder
│   ├── executor.py          # Playwright Subprocess Runner & Artifact Capture
│   └── healer.py            # Failure Signature Analyzer & Code Correction Engine
├── workspace/               # Isolated Playwright Execution Sandbox Environment
│   ├── package.json
│   ├── playwright.config.js
│   ├── pages/               # Dynamically generated Page Object Models
│   ├── tests/               # Executable Playwright Spec Layouts
│   └── reports/
│       └── dashboard.html   # Local Control Center, Test Executor, & Analytics HUD
└── requirements.txt         # System Dependency Manifest Tree