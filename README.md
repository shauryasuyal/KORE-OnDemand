# Kore: The OnDemand AI Desktop Assistant

**Kore** is an advanced AI-powered desktop assistant for Windows that brings a friendly, intelligent companion to your computer. Built explicitly for the **OnDemand Track**, Kore combines natural language understanding with deep system integration, controlling your PC through a sophisticated **Multi-Agent Swarm**.

## OnDemand Track Compliance & Architecture

Our project strictly adheres to and exceeds the technical requirements outlined in the OnDemand guidelines.

### 1. Multi-Agent Architecture (Exceeds Requirements)
**Requirement:** The system must demonstrate integration of at least six (6) agents.
**Our Implementation:** We have orchestrated **7 specialized agents** to ensure a clear separation of concerns:

* **Agent 1 - KERBEROS (Command Router):** The central brain that analyzes user commands and routes them to the correct specialist.
* **Agent 2 - File Navigator:** Specialized in file/folder operations (search, create, delete, move).
* **Agent 3 - System Monitor:** Tracks CPU, RAM, disk space, and processes for performance diagnostics.
* **Agent 4 - Web Research:** Optimizes Google searches and retrieves online documentation/drivers.
* **Agent 5 - Code Assistant:** Executes terminal commands and manages Git operations.
* **Agent 6 - Visual AI:** Analyzes screenshots and detects UI elements.
* **Agent 7 - DLL Troubleshooter:** Automates the repair of missing DLL errors.

### 2. Custom Tool Integrations (Meets Requirements)
**Requirement:** Each project must include a minimum of three (3) different custom-built tool integrations.
**Our Implementation:** We built **3 custom tools** to enable deep OS interaction:

* **Tool 1 - Windows Control API:** Launches apps, opens folders, runs terminal commands, and kills processes.
* **Tool 2 - File Operations API:** Performs system-wide file searches and smart organization by file type.
* **Tool 3 - System Query API:** Provides real-time system metrics, process monitoring, and health checks.

### 3. Mandatory API Integrations (Meets Requirements)
**Requirement:** Projects must integrate the Chat API and Media API.

**Our Implementation:**

* **Chat API:** Powers the core real-time communication session between the user and our agent swarm.
* **Media API:** Enables the **Visual AI** agent to upload and analyze screenshots for visual task verification and error detection.

---

## Key Features & OnDemand Usage

### Self-Healing System (Flagship Feature)
The standout capability of Kore is its ability to autonomously detect and resolve system errors.
* **OnDemand Components:** **Agent 7 (DLL Troubleshooter)**, **Agent 4 (Web Research)**, **Tool 1 (Windows Control)**.
* **Workflow:**
    1.  **Visual AI (Agent 6)** scans the screen via the **Media API** to identify error pop-ups.
    2.  **Agent 7** initiates a fix protocol, using **Agent 4** to scrape the web for the correct drivers/DLLs.
    3.  **Tool 1** downloads, extracts, and installs the file into protected Windows System32 directories.

### Multimodal Interaction & Routing
Talk to Kore like a friend, or type commands if you prefer silence.
* **OnDemand Components:** **Chat API**, **Agent 1 (KERBEROS)**.
* **Workflow:** All inputs are processed via the **Chat API** and sent to **KERBEROS**, which routes complex intents (like "fix my wifi" vs. "organize my files") to the correct agent.

### OS-Level Automation & Organization
Kore performs complex file operations and system cleaning.
* **OnDemand Components:** **Agent 2 (File Navigator)**, **Tool 2 (File Operations)**.
* **Workflow:** The **File Operations API** scans the desktop and segregates files by metadata types (Images, Docs), while **Agent 2** handles universal search.

---

## Links & Demo

**Demo Video:** [Watch on Vimeo](https://vimeo.com/manage/videos/1156404546) - *Demonstrates core functionality and agent interactions *

## Screenshots

**Overlay**
![App Screenshot](https://i.postimg.cc/NGVpwJQL/6d9293b2-309c-459b-b6bc-6eaf117770d1.png)

**Speech Recognition Active**
![App Screenshot](https://i.postimg.cc/xjkBHbCd/5444ac09-6703-444a-9bc1-4ce0b678f09b.png)

**Fixing DLL issues (Powered by Agent 7)**
![App Screenshot](https://i.postimg.cc/QxF5TZ2v/Screenshot-2026-01-20-at-2-27-30-PM.png)

## Authors
* [@shauryasuyal](https://github.com/shauryasuyal)
* [@vedantawasthi](https://github.com/VedantAwasthi-26)
* [@ujjawalkishor](https://github.com/meltingboiling)
* [@paarthgupta](https://github.com/Paarthgupta-coder)
