@echo off
cd /d d:\g_automation_ai
echo Starting G_Automation_AI Server...
echo Open http://localhost:8000 in your browser
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
