# G_Automation_AI v2 — Complete User Guide

> **Automated Test Case Generation & Execution Powered by AI**

---

## 📖 Table of Contents

1. [What Is This Application?](#-what-is-this-application)
2. [How to Start the Application](#-how-to-start-the-application)
3. [Understanding the User Interface](#-understanding-the-user-interface)
4. [Workflow Overview — 5 Simple Steps](#-workflow-overview--5-simple-steps)
5. [Method 1: Using Prompt Tab (Describe in Plain English)](#method-1-using-the-prompt-tab)
6. [Method 2: Using Document Upload Tab](#method-2-using-the-document-upload-tab)
7. [Data Configuration Explained](#-data-configuration-explained)
8. [Browser Mode — Manual Test Case Builder](#-browser-mode--manual-test-case-builder)
9. [What Happens After You Click Generate?](#-what-happens-after-you-click-generate)
10. [Execution, Healing & Reports](#-execution-healing--reports)
11. [Tips & Troubleshooting](#-tips--troubleshooting)

---

## 🤖 What Is This Application?

**G_Automation_AI** is a smart tool that uses **Artificial Intelligence (AI)** to automatically create and run software tests for websites.

### What can it do?

| Feature | Description |
|---------|-------------|
| **Generate Tests from Plain English** | You describe what to test, AI creates the test cases |
| **Generate Tests from Documents** | Upload Word, PDF, or Excel files — AI extracts test cases |
| **Manual Test Entry (Browser Mode)** | You type in your own test cases manually |
| **Auto-Generate Scripts** | Creates Playwright automation scripts (POM-based) |
| **Execute Tests Automatically** | Runs the tests on real websites |
| **Self-Healing** | If a test breaks due to code changes, AI tries to fix it |
| **Detailed Reports** | Generates HTML and CSV reports with results |

---

## 🚀 How to Start the Application

### Step 1: Open Command Prompt
Press `Windows + R`, type `cmd`, and press Enter.

### Step 2: Navigate to the Application Folder
```cmd
cd d:\g_automation_ai
```

### Step 3: Activate the Virtual Environment
```cmd
venv\Scripts\activate
```
> You should see `(venv)` appear at the beginning of the command line.

### Step 4: Start the Server
```cmd
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Open Your Browser
Go to: **http://localhost:8000**

---

## 🖥️ Understanding the User Interface

When you open the application, you'll see:

```
┌─────────────────────────────────────────────────────────┐
│  G_Automation_AI v2                      ● Local · Ollama │
├─────────────────────────────────────────────────────────┤
│  1. Input │ 2. Review Tests │ 3. Generate │ 4. Execute │ 5. Report │
├─────────────────────────────────────────────────────────┤
│  [Prompt]  [Upload Document]  [History]                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 📝 Enter Test Scenario                          │    │
│  │ ┌─────────────────────────────────────────┐    │    │
│  │ │ Describe what you want to test...       │    │    │
│  │ └─────────────────────────────────────────┘    │    │
│  │ [Target Environment: dev ▼] [Retry Cap: 3]     │    │
│  │ ☐ Enable DOM Inspection                        │    │
│  │ [Attach Screenshots (optional)]                 │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ ⚙️ Data Configuration                          │    │
│  │ [📄 Inline] [📊 Data-driven] [🖥️ Browser Mode]  │    │
│  │                                                 │    │
│  │ (Content changes based on selected mode)        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  [🤖 Generate Test Cases with AI]                       │
└─────────────────────────────────────────────────────────┘
```

### Navigation Elements

| Element | Purpose |
|---------|---------|
| **Steps Bar** (1-5) | Shows your progress through the workflow |
| **Tabs** (Prompt / Upload Document / History) | Choose how to input your test requirements |
| **Results Area** | Shows generated test cases, scripts, and reports |

---

## 🔄 Workflow Overview — 5 Simple Steps

```
Step 1          Step 2            Step 3            Step 4            Step 5
───────    ───────────────    ─────────────    ───────────────    ──────────
INPUT   →   REVIEW TESTS   →   GENERATE      →   EXECUTE &      →   REPORT
                                      SCRIPTS         HEAL
```

| Step | What Happens |
|------|-------------|
| **1. Input** | You describe what to test (via prompt, document, or manual entry) |
| **2. Review Tests** | AI shows you the test cases it created. You can edit them |
| **3. Generate Scripts** | AI creates Playwright automation code |
| **4. Execute & Heal** | Tests run automatically. If they fail, AI tries to fix them |
| **5. Report** | See results, download HTML/CSV reports |

---

## Method 1: Using the Prompt Tab

**Best for:** When you know what to test and can describe it in plain English.

### Step-by-Step Instructions

**Step 1:** Go to the **Prompt** tab (it's selected by default)

**Step 2:** In the text area, type what you want to test. For example:

```
Test the login page of dev.ges.store. 
1. Verify that the page loads with username and password fields
2. Test login with valid credentials (user@test.com / password123)
3. Test login with invalid credentials - should show error message
4. Verify that clicking "Forgot Password" link redirects to reset page
```

**Step 3:** Choose settings:

| Setting | What It Does |
|---------|-------------|
| **Target Environment** | Select `dev` (development) or `uat` (testing) server |
| **Retry Cap** | How many times to retry if a test fails (1-5) |
| **DOM Inspection** | ☑ Check this to let AI analyze the live webpage structure for accurate element detection |
| **Attach Screenshots** | (Optional) Upload screenshots of the page for AI to analyze |

**Step 4:** Choose your **Data Configuration** (explained in next section)

**Step 5:** Click **"Generate Test Cases with AI"**

**Step 6:** Wait for the AI to process (you'll see a loading screen)

**Step 7:** Review the generated test cases. Click **"Confirm & Generate Scripts"**

---

## Method 2: Using the Document Upload Tab

**Best for:** When you have requirements written in a document (Word, PDF, Excel, or Text file).

### Step-by-Step Instructions

**Step 1:** Click on the **Upload Document** tab

**Step 2:** Click **"Choose File"** and select your document

**Supported file types:**
- 📄 **Word documents** (.docx)
- 📕 **PDF files** (.pdf)
- 📝 **Text files** (.txt)
- 📊 **CSV/Excel files** (.csv)

**Step 3:** Set the environment and retry cap

**Step 4:** Optionally enable **DOM Inspection** and attach **Screenshots**

**Step 5:** Choose your **Data Configuration** mode

**Step 6:** Click **"Generate Test Cases with AI"**

**Step 7:** AI will extract text from your document and create test cases

---

## ⚙️ Data Configuration Explained

The **Data Configuration** section lets you choose **how** the AI handles test data.

### 1. 📄 Inline Mode (Default)

**How it works:**
- Test data is extracted directly from your prompt or document
- AI analyzes the text and automatically creates test cases
- No additional files needed

**Use when:** Your prompt or document already contains all the necessary information

---

### 2. 📊 Data-driven Mode

**How it works:**
- You upload a separate data file (Excel/CSV) containing test data
- AI reads the data and creates test cases for each row
- Great for testing the same scenario with different inputs

**Example CSV file:**
```csv
username,password,expected_result
user@test.com,password123,login_success
user@test.com,wrongpass,login_failed
invalid@user,password123,login_failed
```

**Step-by-step:**
1. Click **"Data-driven"** button
2. Click the upload area to select your Excel/CSV file
3. AI will create test cases for each data row

---

### 3. 🖥️ Browser Mode (Manual Entry)

**How it works:**
- You manually type in your own test cases
- AI directly generates Playwright automation scripts
- No AI test generation — you're in full control

**When to use:**
- You already have written test cases
- You want specific test cases that you define
- You need to test edge cases not covered by AI generation

**Step-by-step:**
1. Click **"Browser Mode"** button
2. Click **"Add Test Case"**
3. Fill in the details:
   - **Title**: e.g., "Verify login with valid credentials"
   - **Description**: e.g., "Test that user can login with correct username and password"
   - **Steps**: One step per line
     ```
     Navigate to login page
     Enter username "user@test.com"
     Enter password "password123"
     Click login button
     ```
   - **Expected Result**: e.g., "User is redirected to dashboard"
4. Add as many test cases as you need
5. Click **"Generate Playwright Scripts from Manual Tests"**

---

## 🔧 What Happens After You Click Generate?

### Behind the Scenes

```
Your Input (Prompt/Document/Manual)
        │
        ▼
    ┌─────────────────┐
    │  AI (Ollama)    │
    │  - Analyzes input│
    │  - Creates test  │
    │    cases         │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Test Cases     │  ← You review these
    │  Generated      │
    └────────┬────────┘
             │ (You click "Confirm")
             ▼
    ┌─────────────────┐
    │  Playwright     │
    │  Scripts        │  ← Automation code created
    │  (POM-based)    │
    └────────┬────────┘
             │ (You click "Execute")
             ▼
    ┌─────────────────┐
    │  Test Execution │
    │  - Runs on real │
    │    website      │
    │  - If fails, AI │
    │    tries to fix │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Report         │  ← Download HTML/CSV
    │  Generated      │
    └─────────────────┘
```

### Step 1: After Clicking "Generate Test Cases"

- A **loading overlay** appears (you can't click anything else)
- AI processes your input using **Ollama** (local AI running on your computer)
- Generated test cases appear in the **Results Area**

### Step 2: Review Test Cases

You'll see something like this:

```
┌──────────────────────────────────────────────────────┐
│  Generated Manual Test Cases                        │
│                                                      │
│  Environment: dev | Data Mode: inline | Retry: 3    │
│                                                      │
│  ┌────────────────────────────────────────────┐     │
│  │ TC_1: Verify page loads                    │     │
│  │ Check that the login page loads            │     │
│  │ Steps: 1. Navigate to the URL              │     │
│  │         2. Wait for page to load           │     │
│  │ Expected: Page loads within 10 seconds     │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  [✓ Confirm & Generate Scripts]  [✏ Edit]  [↺ Start Over] │
└──────────────────────────────────────────────────────┘
```

**You can:**
- ✅ **Confirm** — Accept test cases and generate scripts
- ✏️ **Edit** — Modify test cases inline before confirming
- ↺ **Start Over** — Go back to the beginning

### Step 3: Script Generation

After confirming:
- AI creates **Page Object Model (POM)** scripts
- You'll see the **Page Object** code and **Test Spec** code
- You can **download** the scripts

---

## 📊 Execution, Healing & Reports

### Running Tests

Click **"Execute Tests"** to run the generated scripts on the actual website.

### Possible Results

| Result | Meaning |
|--------|---------|
| ✅ **PASSED** | All tests ran successfully |
| 🔧 **HEALED & PASSED** | Tests failed initially, AI fixed them, and they passed |
| ❌ **APPLICATION DEFECT** | The bug is in the website itself, not the test |
| ❌ **ENVIRONMENT ISSUE** | The test environment has a problem |
| 🔍 **NEEDS MANUAL REVIEW** | AI couldn't fix the issue — needs human help |

### Self-Healing Feature

If a test fails, AI tries to fix it by:

1. **Checking the error** — Is it a script issue, application bug, or environment problem?
2. **If script issue** — AI tries multiple strategies to fix the locators/selectors
3. **Updating the code** — AI rewrites the failing script
4. **Re-running** — Up to your specified "Retry Cap" times

### Reports

After execution, you can download:
- 📄 **HTML Report** — Visual report with detailed results
- 📊 **CSV Report** — Spreadsheet-compatible data

---

## 💡 Tips & Troubleshooting

### Best Practices

| Tip | Description |
|-----|-------------|
| **Be specific in prompts** | "Test login with valid and invalid credentials" is better than "Test the website" |
| **Use DOM Inspection** | Check this for more accurate element selectors |
| **Keep Retry Cap at 3** | This is the sweet spot between speed and reliability |
| **Use Browser Mode for complex scenarios** | If AI-generated tests aren't quite right, manually create them |

### Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Connection refused" error** | Make sure Ollama is running (`ollama serve`) |
| **No test cases generated** | Try being more specific in your prompt |
| **Tests failing consistently** | Check if the website is accessible |
| **Slow performance** | First run is always slower as models load |
| **Loader stays forever** | Refresh the page and try again |

---

## 🎯 Summary

```
┌─────────────────────────────────────────────────────┐
│              G_Automation_AI v2                     │
│                                                     │
│  INPUT METHODS:                                     │
│  ┌─────────┐  ┌────────────────┐  ┌─────────────┐  │
│  │ Prompt  │  │ Upload Document│  │ Browser Mode│  │
│  │ (Plain  │  │ (Word/PDF/TXT/ │  │ (Manual Test│  │
│  │ English)│  │  CSV/Excel)    │  │  Entry)     │  │
│  └────┬────┘  └───────┬────────┘  └──────┬──────┘  │
│       └───────────────┼──────────────────┘          │
│                       ▼                             │
│              ┌────────────────┐                     │
│              │  AI Generates  │                     │
│              │  Test Cases    │                     │
│              └───────┬────────┘                     │
│                       ▼                             │
│              ┌────────────────┐                     │
│              │ You Review &   │                     │
│              │ Confirm/Edit   │                     │
│              └───────┬────────┘                     │
│                       ▼                             │
│              ┌────────────────┐                     │
│              │ AI Generates   │                     │
│              │ Playwright     │                     │
│              │ Scripts (POM)  │                     │
│              └───────┬────────┘                     │
│                       ▼                             │
│              ┌────────────────┐                     │
│              │ Execute Tests  │                     │
│              │ Auto-Heal if   │                     │
│              │ needed         │                     │
│              └───────┬────────┘                     │
│                       ▼                             │
│              ┌────────────────┐                     │
│              │ Download       │                     │
│              │ HTML/CSV       │                     │
│              │ Report         │                     │
│              └────────────────┘                     │
└─────────────────────────────────────────────────────┘
```

---

*For technical support, check the `TODO.md` file or refer to the project documentation.*

*Generated by G_Automation_AI v2 — Last updated: December 2024*

