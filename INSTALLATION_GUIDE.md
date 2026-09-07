# G_Automation_AI v2 — Step-by-Step Installation Guide

> **Complete installation guide for setting up the AI-powered Test Automation System**

---

## 📋 Table of Contents

1. [System Requirements](#-system-requirements)
2. [Prerequisites Installation](#-prerequisites-installation)
   - [Step 1: Install Python 3.12+](#step-1-install-python-312)
   - [Step 2: Install Node.js 18+](#step-2-install-nodejs-18)
   - [Step 3: Install Ollama AI](#step-3-install-ollama-ai)
   - [Step 4: Pull Required AI Models](#step-4-pull-required-ai-models)
3. [Project Setup](#-project-setup)
   - [Step 5: Set Up Python Virtual Environment](#step-5-set-up-python-virtual-environment)
   - [Step 6: Install Python Dependencies](#step-6-install-python-dependencies)
   - [Step 7: Install Node.js Dependencies](#step-7-install-nodejs-dependencies)
   - [Step 8: Install Playwright Browsers](#step-8-install-playwright-browsers)
   - [Step 9: Install Tesseract OCR (Optional)](#step-9-install-tesseract-ocr-optional)
4. [Running the Application](#-running-the-application)
   - [Step 10: Start Ollama Server](#step-10-start-ollama-server)
   - [Step 11: Start the Application Server](#step-11-start-the-application-server)
   - [Step 12: Open the Application](#step-12-open-the-application)
5. [Quick Start Test Drive](#-quick-start-test-drive)
6. [Troubleshooting](#-troubleshooting)

---

## 💻 System Requirements

| Component | Minimum Requirement |
|-----------|-------------------|
| **OS** | Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+) |
| **CPU** | 4+ cores (8+ recommended for AI models) |
| **RAM** | 8 GB minimum (16 GB recommended) |
| **Storage** | 15 GB free space (for AI models + dependencies) |
| **Internet** | Required for downloading dependencies and AI models |

---

## 🔧 Prerequisites Installation

### Step 1: Install Python 3.12+

**Check if Python is already installed:**
```cmd
python --version
```
You should see `Python 3.12.x` or higher.

**If not installed:**

**Windows:**
1. Go to [python.org/downloads](https://python.org/downloads)
2. Download **Python 3.12.x** (or latest stable)
3. **IMPORTANT:** Check ✅ **"Add Python to PATH"** during installation
4. Click **Install Now**
5. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

**macOS:**
```bash
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip -y
```

---

### Step 2: Install Node.js 18+

**Check if Node.js is already installed:**
```cmd
node --version
npm --version
```
You should see `v18.x.x` or higher for Node.js.

**If not installed:**

**Windows:**
1. Go to [nodejs.org](https://nodejs.org)
2. Download the **LTS** version (18.x or 20.x)
3. Run the installer (all default options are fine)
4. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

**macOS:**
```bash
brew install node@18
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

---

### Step 3: Install Ollama AI

**Windows:**
1. Go to [ollama.com/download](https://ollama.com/download)
2. Download the Windows installer
3. Run the installer (Ollama will run as a system service)
4. After installation, Ollama starts automatically in the system tray
5. Verify by opening a terminal:
   ```cmd
   ollama --version
   ```

**macOS:**
```bash
brew install ollama
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

### Step 4: Pull Required AI Models

The application uses **3 different AI models** for different tasks. Open a terminal and pull them:

**Model 1 — Test Case Generator (General reasoning):**
```cmd
ollama pull llama3:latest
```
> ⏱ **Time:** 3-10 minutes (4.7 GB download)

**Model 2 — Code Generator (Code-tuned for POM scripts):**
```cmd
ollama pull qwen2.5-coder:7b
```
> ⏱ **Time:** 3-10 minutes (4.7 GB download)

**Model 3 — Vision Model (For screenshot/image analysis):**
```cmd
ollama pull moondream:latest
```
> ⏱ **Time:** 1-3 minutes (1.6 GB download)

**Verify all models are installed:**
```cmd
ollama list
```
You should see all three models listed.

> ⚠️ **Total download size:** ~11 GB. Make sure you have a stable internet connection.
>
> 💡 **Alternative (lighter models):** If you have limited resources, you can modify `app/agent.py` to use smaller models:
> - Replace `llama3:latest` with `llama3.2:3b` (2 GB)
> - Replace `qwen2.5-coder:7b` with `qwen2.5-coder:1.5b` (1 GB)
> - Replace `moondream:latest` with `llava:7b` (4.5 GB)

---

## 📁 Project Setup

### Step 5: Set Up Python Virtual Environment

Navigate to the project root and create a virtual environment:

```cmd
cd d:\g_automation_ai
python -m venv venv
```

**Activate the virtual environment:**

**Windows:**
```cmd
venv\Scripts\activate
```
> You should see `(venv)` appearing at the beginning of the command line.

**macOS/Linux:**
```bash
source venv/bin/activate
```

---

### Step 6: Install Python Dependencies

With the virtual environment **activated**, install the required packages:

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

**What gets installed:**
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | ≥0.115.0 | Web API framework |
| `uvicorn` | ≥0.30.1 | ASGI server (runs the app) |
| `pydantic` | ≥2.12.0 | Data validation |
| `python-multipart` | ≥0.0.12 | File upload support |
| `requests` | ≥2.32.3 | HTTP requests |
| `ollama` | ≥0.2.1 | Python client for Ollama AI |
| `sqlalchemy` | ≥2.0.30 | Database ORM (SQLite) |
| `docx2txt` | ==0.8 | Word document parsing |
| `pypdf` | ≥4.2.0 | PDF file parsing |
| `pillow` | ≥11.0.0 | Image processing |
| `pytesseract` | ≥0.3.10 | OCR (text extraction from images) |

> ⏱ **Time:** 2-5 minutes depending on internet speed.

---

### Step 7: Install Node.js Dependencies

Open a **new terminal** (or keep the same one) and navigate to the workspace:

```cmd
cd d:\g_automation_ai\workspace
npm install
```

> ⏱ **Time:** 1-3 minutes.
>
> This installs **Playwright** (`@playwright/test`) and its dependencies.

---

### Step 8: Install Playwright Browsers

Playwright needs browser binaries to run tests. From the workspace directory:

```cmd
cd d:\g_automation_ai\workspace
npx playwright install chromium
```

> ⏱ **Time:** 1-3 minutes (~200 MB download).
>
> This downloads the **Chromium** browser that Playwright will use for test execution.

**Verify Playwright is working:**
```cmd
npx playwright --version
```
You should see a version number (e.g., `1.62.0`).

---

### Step 9: Install Tesseract OCR (Optional)

**Only needed if you plan to upload screenshots with text for OCR analysis.**

**Windows:**
1. Go to [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Download the 64-bit installer (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`)
3. Run the installer
4. **Important:** Note the installation path (default: `C:\Program Files\Tesseract-OCR`)
5. Add to system PATH:
   - Open **System Properties** → **Environment Variables**
   - Under **System variables**, find `Path`, click **Edit**
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click **OK** on all dialogs
6. Verify:
   ```cmd
   tesseract --version
   ```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install tesseract-ocr -y
```

---

## 🚀 Running the Application

### Step 10: Start Ollama Server

Ollama must be running in the background before starting the application.

**Windows:** Ollama starts automatically as a system service. Check the system tray for the Ollama icon (llama icon).

**If it's not running, start it manually:**
```cmd
ollama serve
```
> Keep this terminal window open — Ollama must stay running.

**Verify Ollama is running:**
```cmd
ollama list
```
You should see your three models listed.

---

### Step 11: Start the Application Server

**Option A — Using the batch file (Windows only):**
```cmd
cd d:\g_automation_ai
run_server.bat
```

**Option B — Manually:**

Make sure your virtual environment is activated:
```cmd
cd d:\g_automation_ai
venv\Scripts\activate
```

Then start the server:
```cmd
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> **What you should see:**
> ```
> INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
> INFO:     Started reloader process [12345] using WatchFiles
> INFO:     Started server process [12346]
> INFO:     Waiting for application startup.
> INFO:     Application startup complete.
> ```

---

### Step 12: Open the Application

Open your web browser and go to:

**👉 [http://localhost:8000](http://localhost:8000)**

You should see the **G_Automation_AI v2** user interface with:
- A **navbar** showing "G_Automation_AI v2" and "Local · Ollama" status
- **Steps bar** (1. Input → 2. Review Tests → 3. Generate Scripts → 4. Execute & Heal → 5. Report)
- **Tabs**: Prompt | Upload Document | History
- Input fields, environment selector, and the **"Generate Test Cases with AI"** button

![Application UI](https://via.placeholder.com/800x450?text=G_Automation_AI+v2+UI)

---

## 🎯 Quick Start Test Drive

Once everything is installed and running, try this quick test:

### Test with a simple prompt:

1. In the **Prompt** tab, enter:
   ```
   Test the login page. Try login with valid credentials and invalid credentials. Check forgot password link works.
   ```

2. Set **Target Environment** to `dev`

3. Leave **Retry Cap** at `3`

4. Click **"🤖 Generate Test Cases with AI"**

5. Wait 10-30 seconds for AI to process

6. Review the generated test cases

7. Click **"✓ Confirm & Generate Scripts"**

8. Review the generated Playwright scripts

9. Click **"▶ Execute Tests"** to run them

10. View the results and download reports

---

## 🔧 Troubleshooting

### Common Installation Issues

| Problem | Solution |
|---------|----------|
| **`python` not recognized** | Python is not in PATH. Reinstall Python with "Add to PATH" checked |
| **`pip` not recognized** | Reinstall Python and ensure "pip" is included |
| **`node` not recognized** | Node.js is not in PATH. Reinstall Node.js with default options |
| **`ollama` not recognized** | Restart your terminal after installing Ollama |
| **Virtual environment activation fails** | On Windows, try `venv\Scripts\activate.bat` or use PowerShell |
| **`pip install` fails with long paths** | Run `pip install --no-cache-dir -r requirements.txt` |
| **Port 8000 already in use** | Change port: `uvicorn app.main:app --host 0.0.0.0 --port 8001` |
| **Ollama connection refused** | Make sure `ollama serve` is running in a separate terminal |

### Application Startup Issues

| Error | Solution |
|-------|----------|
| **"ModuleNotFoundError: No module named 'app'"** | Make sure you're running from the project root (`d:\g_automation_ai`) |
| **"Connection refused" when generating tests** | Ensure Ollama is running (`ollama serve`) |
| **Tests fail with "Target URL unreachable"** | Check if the target website is accessible from your network |
| **No test cases generated (blank result)** | Try a more detailed prompt. Check Ollama is running |
| **Loader stays spinning forever** | Refresh the page and try again. Check terminal for errors |

### Performance Notes

- **First run is slower:** AI models need to load into memory. First request may take 30-60 seconds.
- **Subsequent runs:** 10-30 seconds per generation.
- **Ollama resource usage:** AI models use 4-8 GB of RAM collectively.
- **If your system is low on memory:** Use smaller models (see Step 4 alternatives).

---

## 📦 Complete Installation Checklist

Use this to track your progress:

- [ ] **Step 1:** Python 3.12+ installed (`python --version`)
- [ ] **Step 2:** Node.js 18+ installed (`node --version`)
- [ ] **Step 3:** Ollama installed (`ollama --version`)
- [ ] **Step 4a:** `llama3:latest` model pulled (`ollama pull llama3:latest`)
- [ ] **Step 4b:** `qwen2.5-coder:7b` model pulled (`ollama pull qwen2.5-coder:7b`)
- [ ] **Step 4c:** `moondream:latest` model pulled (`ollama pull moondream:latest`)
- [ ] **Step 5:** Python virtual environment created and activated
- [ ] **Step 6:** Python dependencies installed (`pip install -r requirements.txt`)
- [ ] **Step 7:** Node.js dependencies installed (`npm install` in workspace/)
- [ ] **Step 8:** Playwright Chromium installed (`npx playwright install chromium`)
- [ ] **Step 9:** Tesseract OCR installed (optional)
- [ ] **Step 10:** Ollama server running (`ollama serve`)
- [ ] **Step 11:** Application server running (`uvicorn app.main:app --port 8000`)
- [ ] **Step 12:** Open [http://localhost:8000](http://localhost:8000) in browser

---

## ❓ Need Help?

Check these resources:
- **User Guide:** `USER_GUIDE.md` — Detailed usage instructions
- **Project Structure:** `Project Structure.MD` — File/folder organization
- **TODO:** `TODO.md` — Known issues and planned improvements
- **Ollama Docs:** [github.com/ollama/ollama](https://github.com/ollama/ollama)
- **Playwright Docs:** [playwright.dev](https://playwright.dev/docs/intro)

---

*Installation Guide v1.0 — Generated for G_Automation_AI v2*

