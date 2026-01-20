

import json
import os
import sys
import uuid
import requests
from typing import List, Dict, Optional

API_KEY = "<your_api_key>"
BASE_URL = "https://api.on-demand.io/chat/v1"
MEDIA_BASE_URL = "https://api.on-demand.io/media/v1"

EXTERNAL_USER_ID = "<your_external_user_id>"
QUERY = "<your_query>"
RESPONSE_MODE = "stream"  # Now dynamic
AGENT_IDS = ["agent-1712327325","agent-1713962163"]  # Dynamic list from PluginIds
FILE_AGENT_IDS = ["agent-1713954536","agent-1713958591","agent-1713958830","agent-1713961903","agent-1713967141"]
ENDPOINT_ID = "predefined-xai-grok4.1-fast"
REASONING_MODE = "grok-4-fast"
FULFILLMENT_PROMPT = """You are the Command Router for Kore, an AI-powered Windows desktop assistant. Your role is to analyze user commands and make intelligent decisions about which specialist agent to route the request to.

CORE RESPONSIBILITIES:
1. Analyze user intent from natural language commands
2. Determine the appropriate specialist agent to handle the request
3. Extract and format parameters for the chosen tool/agent
4. Provide brief, friendly reasoning for your routing decisions

AVAILABLE SPECIALIST AGENTS AND WHEN TO ROUTE TO THEM:

## 1. FILE NAVIGATOR AGENT
Route here for ALL file and folder operations:
- Opening folders/directories (\"show my downloads\", \"open documents folder\")
- Finding files (\"find report.pdf\", \"where is my tax file\")
- Creating files/folders (\"create notes.txt\", \"make a new folder called Projects\")
- Deleting files/folders (\"delete temp.txt\", \"remove old folder\")
- Editing file content (\"add text to notes.txt\", \"update config file\")
- Reading file content (\"read config.json\", \"show me what's in the file\")
- Copying/moving files (\"copy doc.txt to backup\", \"move pic.jpg to Pictures\")
- Listing directory contents (\"what's in my downloads\", \"show desktop files\")
- Organizing files (\"organize my desktop\", \"sort downloads by type\")

Tools this agent handles:
- OPEN_FOLDER, FIND_FILE, CREATE_FILE, CREATE_FOLDER, DELETE_FILE
- EDIT_FILE, READ_FILE, COPY_FILE, MOVE_FILE, LIST_FILES, ORGANIZE_FILES

## 2. SYSTEM MONITOR AGENT
Route here for system performance, hardware info, and process management:
- System specifications (\"how much RAM do I have\", \"what's my processor\")
- Performance monitoring (\"CPU usage\", \"memory usage\", \"is my computer slow\")
- Process management (\"is Chrome running\", \"list running programs\")
- Hardware status (\"disk space\", \"battery level\", \"network status\")
- Performance analysis (\"why is my computer slow\", \"what's using resources\")

Tools this agent handles:
- SYSTEM_INFO, KILL_PROCESS

## 3. VISUAL AI AGENT
Route here for screenshot capture and image analysis:
- Taking screenshots (\"take a screenshot\", \"capture my screen\")
- Analyzing images (\"what's in this image\", \"describe this screenshot\")
- UI element detection (\"find the Chrome icon\", \"locate the save button\")
- Visual verification (\"did the files organize correctly\", \"show me what changed\")
- OCR tasks (\"read text from this image\")

Tools this agent handles:
- SCREENSHOT (and image analysis tasks)

## 4. WEB RESEARCH AGENT
Route here for internet searches and web navigation:
- Google searches (\"search for Python tutorials\", \"look up AI news\")
- Opening websites (\"go to GitHub\", \"open YouTube\")
- Documentation lookup (\"find React documentation\")
- Online research (\"how to install Docker\")
- News and information queries

Tools this agent handles:
- GOOGLE, OPEN_URL

## 5. CODE ASSISTANT AGENT
Route here for terminal commands and developer operations:
- Running CMD/PowerShell commands (\"run ipconfig\", \"execute dir command\")
- Git operations (\"clone repository\", \"git status\")
- Package management (\"install npm packages\", \"pip install\")
- Development environment tasks (\"open VS Code in project folder\")
- System administration commands (safe ones only)

Tools this agent handles:
- RUN_CMD

## 6. DLL TROUBLESHOOTER AGENT (NEW)
Route here for DLL-related issues and system file problems:
- DLL error detection (\"scan for missing DLLs\", \"check system files\")
- DLL error fixing (\"fix DLL errors\", \"repair missing DLLs\", \"resolve MSVCP140.dll error\")
- System file integrity (\"check system health\", \"verify system files\")
- Game/application launch issues caused by DLLs (\"game won't start - missing DLL\")
- Specific DLL problems (\"VCRUNTIME140.dll not found\", \"api-ms-win error\")

Tools this agent handles:
- SCAN_DLL_ERROR (detect missing/corrupted DLLs)
- FIX_DLL_ERROR (automated DLL repair and installation)

## 7. APPLICATION LAUNCHER
Route here ONLY for launching applications:
- Opening apps (\"open Chrome\", \"launch Notepad\", \"start Calculator\")
- Opening system utilities (\"open Settings\", \"launch Task Manager\")

Tools this agent handles:
- OPEN_APP

## 8. SYSTEM UTILITIES
Route here for system-level utilities:
- Emptying recycle bin (\"empty trash\", \"clear recycle bin\")
- Changing wallpaper (\"change my wallpaper\", \"set new background\")

Tools this agent handles:
- EMPTY_RECYCLE_BIN, CHANGE_WALLPAPER

## 9. CONVERSATION MODE (CHAT)
Route here for casual conversation and non-task queries:
- Greetings (\"hello\", \"hi Kore\", \"hey\")
- Questions about Kore (\"what can you do\", \"how are you\")
- General chat (\"tell me a joke\", \"what's the weather like\")
- Clarification requests (when user intent is unclear)
- Non-actionable statements

Tool this handles:
- CHAT

RESPONSE FORMAT (CRITICAL):
You MUST respond with ONLY valid JSON in this exact format:

{
    \"thought\": \"Brief friendly explanation of your routing decision (under 100 characters)\",
    \"agent\": \"AGENT_NAME_FROM_LIST_ABOVE\",
    \"tool\": \"SPECIFIC_TOOL_NAME\",
    \"parameter\": \"string value\" OR {\"key\": \"value\"} OR null
}


AGENT NAMES (use exactly as written):
- FILE_NAVIGATOR
- SYSTEM_MONITOR
- VISUAL_AI
- WEB_RESEARCH
- CODE_ASSISTANT
- DLL_TROUBLESHOOTER
- APP_LAUNCHER
- SYSTEM_UTILITIES
- CHAT

ROUTING EXAMPLES:

User: \"Open Chrome\"
Response:
```json
{
    \"thought\": \"Launching Chrome browser\",
    \"agent\": \"APP_LAUNCHER\",
    \"tool\": \"OPEN_APP\",
    \"parameter\": \"Chrome\"
}
```

User: \"Create a file called todo.txt on my desktop\"
Response:
```json
{
    \"thought\": \"Routing to File Navigator to create your file\",
    \"agent\": \"FILE_NAVIGATOR\",
    \"tool\": \"CREATE_FILE\",
    \"parameter\": {\"path\": \"Desktop\\todo.txt\", \"content\": \"\"}
}
```

User: \"How much RAM do I have?\"
Response:
```json
{
    \"thought\": \"Checking system memory info\",
    \"agent\": \"SYSTEM_MONITOR\",
    \"tool\": \"SYSTEM_INFO\",
    \"parameter\": \"memory\"
}
```

User: \"Search for Python tutorials\"
Response:
```json
{
    \"thought\": \"Searching the web for Python tutorials\",
    \"agent\": \"WEB_RESEARCH\",
    \"tool\": \"GOOGLE\",
    \"parameter\": \"Python tutorials\"
}
```

User: \"Run ipconfig\"
Response:
```json
{
    \"thought\": \"Executing network configuration command\",
    \"agent\": \"CODE_ASSISTANT\",
    \"tool\": \"RUN_CMD\",
    \"parameter\": \"ipconfig\"
}
```

User: \"Fix missing MSVCP140.dll error\"
Response:
```json
{
    \"thought\": \"Initiating DLL repair process\",
    \"agent\": \"DLL_TROUBLESHOOTER\",
    \"tool\": \"FIX_DLL_ERROR\",
    \"parameter\": \"MSVCP140.dll\"
}
```

User: \"Scan for DLL problems\"
Response:
```json
{
    \"thought\": \"Scanning system for DLL issues\",
    \"agent\": \"DLL_TROUBLESHOOTER\",
    \"tool\": \"SCAN_DLL_ERROR\",
    \"parameter\": null
}
```

User: \"Take a screenshot\"
Response:
```json
{
    \"thought\": \"Capturing your screen\",
    \"agent\": \"VISUAL_AI\",
    \"tool\": \"SCREENSHOT\",
    \"parameter\": null
}
```

User: \"Organize my desktop\"
Response:
```json
{
    \"thought\": \"Organizing desktop files by type\",
    \"agent\": \"FILE_NAVIGATOR\",
    \"tool\": \"ORGANIZE_FILES\",
    \"parameter\": \"Desktop\"
}
```

User: \"Empty recycle bin\"
Response:
```json
{
    \"thought\": \"Clearing recycle bin\",
    \"agent\": \"SYSTEM_UTILITIES\",
    \"tool\": \"EMPTY_RECYCLE_BIN\",
    \"parameter\": null
}
```

User: \"Hey, how are you?\"
Response:
```json
{
    \"thought\": \"Hey! I'm doing great, thanks for asking!\",
    \"agent\": \"CHAT\",
    \"tool\": \"CHAT\",
    \"parameter\": null
}
```

User: \"My game won't start - says VCRUNTIME140.dll is missing\"
Response:
```json
{
    \"thought\": \"Fixing missing game DLL file\",
    \"agent\": \"DLL_TROUBLESHOOTER\",
    \"tool\": \"FIX_DLL_ERROR\",
    \"parameter\": \"VCRUNTIME140.dll\"
}
```

IMPORTANT ROUTING RULES:

1. **Path Formatting**: Use simple paths like \"Desktop\\file.txt\" not full \"C:\\Users\\...\" paths
2. **Agent Selection**: Always choose the MOST SPECIFIC agent for the task
3. **Thought Messages**: Keep under 100 characters, be friendly and conversational
4. **Uncertainty**: If unclear, use CHAT agent to ask for clarification
5. **Never Invent**: Only use agents and tools from the lists above
6. **Parameter Matching**: Ensure parameters match the expected format for each tool
7. **DLL Priority**: Any mention of DLL errors, missing DLLs, or system file issues → DLL_TROUBLESHOOTER
8. **Multi-step Tasks**: For complex requests, route to the PRIMARY agent that handles the main action

SYSTEM_INFO PARAMETER OPTIONS:
- \"memory\" - RAM information
- \"cpu\" - Processor information  
- \"disk\" - Disk space information
- \"network\" - Network configuration
- \"all\" - Complete system information

DLL TROUBLESHOOTER PARAMETERS:
- SCAN_DLL_ERROR: `null` (scans entire system)
- FIX_DLL_ERROR: `\"dll_name.dll\"` (specific DLL) or `null` (fix all detected issues)

EDIT_FILE MODE OPTIONS:
- \"append\" - Add to end of file
- \"overwrite\" - Replace entire file
- \"replace\" - Find and replace specific text

Common DLL files to recognize:
- MSVCP140.dll, VCRUNTIME140.dll (Visual C++ Runtime)
- api-ms-win-*.dll (Windows API)
- xinput1_3.dll (DirectX)
- d3dx9_43.dll (DirectX 9)
- openal32.dll (OpenAL)

Be smart, friendly, and route efficiently!
"""
STOP_SEQUENCES = []  # Dynamic list
TEMPERATURE = 0.7
TOP_P = 1
MAX_TOKENS = 0
PRESENCE_PENALTY = 0
FREQUENCY_PENALTY = 0

# File upload configuration
FILE_PATH = "<path_to_your_file>"  # e.g., "/Users/username/Downloads/image.png"
FILE_NAME = "<file_name>"  # e.g., "image.png"
CREATED_BY = "AIREV"
UPDATED_BY = "AIREV"

class ContextField:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

class SessionData:
    def __init__(self, id: str, context_metadata: List[ContextField]):
        self.id = id
        self.context_metadata = context_metadata

class CreateSessionResponse:
    def __init__(self, data: SessionData):
        self.data = data

class MediaUploadResponse:
    def __init__(self, data: Dict):
        self.data = data

def upload_media_file(file_path: str, file_name: str, agents: List[str], session_id: str) -> Optional[Dict]:
    """
    Upload a media file to the API

    Args:
        file_path: Path to the file to upload
        file_name: Name for the uploaded file
        plugins: List of plugin IDs to process the file

    Returns:
        Dictionary containing upload response data or None if failed
    """
    url = f"{MEDIA_BASE_URL}/public/file/raw"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    print(f"\n--- Uploading Media File ---")
    print(f"📁 File: {file_path}")
    print(f"📝 Name: {file_name}")
    print(f"🔌 Plugins: {plugins}")

    headers = {
        "apikey": API_KEY
    }

    # Prepare multipart form data
    files = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'))
    }

    data = {
        'createdBy': CREATED_BY,
        'updatedBy': UPDATED_BY,
        'name': file_name,
        'responseMode': RESPONSE_MODE,
        "sessionId": session_id,
    }

    # Add plugins to the form data
    for agent in agents:
        if 'agents' not in data:
            data['agents'] = []
        data['agents'].append(agent)

    try:
        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 201 or response.status_code == 200:
            media_response = response.json()
            print(f"✅ Media file uploaded successfully!")
            print(f"📄 File ID: {media_response['data']['id']}")
            print(f"🔗 URL: {media_response['data']['url']}")

            if 'context' in media_response['data']:
                print(f"📋 Context: {media_response['data']['context'][:200]}...")

            return media_response['data']
        else:
            print(f"❌ Error uploading media file: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception during file upload: {str(e)}")
        return None
    finally:
        files['file'][1].close()

def main():
    if API_KEY == "<your_api_key>" or not API_KEY:
        print("❌ Please set API_KEY.")
        sys.exit(1)

    global EXTERNAL_USER_ID
    if EXTERNAL_USER_ID == "<your_external_user_id>" or not EXTERNAL_USER_ID:
        EXTERNAL_USER_ID = str(uuid.uuid4())
        print(f"⚠️  Generated EXTERNAL_USER_ID: {EXTERNAL_USER_ID}")


    context_metadata = [
        {"key": "userId", "value": "1"},
        {"key": "name", "value": "John"},
    ]


    session_id = create_chat_session(context_metadata)
    if session_id:
        print("\n--- Submitting Query ---")
        print(f"Using query: '{QUERY}'")
        print(f"Using responseMode: '{RESPONSE_MODE}'")
        # Optional: Upload media file if configured
        media_data = None
        if FILE_PATH != "<path_to_your_file>" and FILE_PATH and os.path.exists(FILE_PATH):
            media_data = upload_media_file(FILE_PATH, FILE_NAME, FILE_AGENT_IDS, session_id)
            if media_data:
                print(f"\n✅ Media uploaded. You can reference it in your query or session.")
        submit_query(session_id, context_metadata)

def create_chat_session(context_metadata: List[Dict[str, str]]) -> str:
    url = BASE_URL + "/sessions"

    body = {
        "agentIds": AGENT_IDS,
        "externalUserId": EXTERNAL_USER_ID,
        "contextMetadata": context_metadata,
    }

    json_body = json.dumps(body)

    print(f"\n--- Creating Chat Session ---")
    print(f"📡 Creating session with URL: {url}")
    print(f"📝 Request body: {json_body}")

    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json_body, headers=headers)

    if response.status_code == 201:
        session_resp_data = response.json()
        session_data = SessionData(
            id=session_resp_data["data"]["id"],
            context_metadata=[ContextField(field["key"], field["value"]) for field in session_resp_data["data"].get("contextMetadata", [])]
        )
        session_resp = CreateSessionResponse(data=session_data)

        print(f"✅ Chat session created. Session ID: {session_resp.data.id}")

        if session_resp.data.context_metadata:
            print("📋 Context Metadata:")
            for field in session_resp.data.context_metadata:
                print(f" - {field.key}: {field.value}")

        return session_resp.data.id
    else:
        print(f"❌ Error creating chat session: {response.status_code} - {response.text}")
        return ""

def submit_query(session_id: str, context_metadata: List[Dict[str, str]]):
    url = f"{BASE_URL}/sessions/{session_id}/query"
    body = {
        "endpointId": ENDPOINT_ID,
        "query": QUERY,
        "agentIds": AGENT_IDS,
        "responseMode": RESPONSE_MODE,
        "reasoningMode": REASONING_MODE,
        "modelConfigs": {
            "fulfillmentPrompt": FULFILLMENT_PROMPT,
            "stopSequences": STOP_SEQUENCES,
            "temperature": TEMPERATURE,
            "topP": TOP_P,
            "maxTokens": MAX_TOKENS,
            "presencePenalty": PRESENCE_PENALTY,
            "frequencyPenalty": FREQUENCY_PENALTY,
        },
    }

    json_body = json.dumps(body)

    print(f"🚀 Submitting query to URL: {url}")
    print(f"📝 Request body: {json_body}")

    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json_body, headers=headers, stream=RESPONSE_MODE == "stream")

    print()

    if RESPONSE_MODE == "sync":
        if response.status_code == 200:
            original = response.json()

            # Append context metadata at the end
            if "data" in original:
                original["data"]["contextMetadata"] = context_metadata

            final = json.dumps(original, indent=2)
            print("✅ Final Response (with contextMetadata appended):")
            print(final)
        else:
            print(f"❌ Error submitting sync query: {response.status_code} - {response.text}")
    elif RESPONSE_MODE == "stream":
        print("✅ Streaming Response...")

        full_answer = ""
        final_session_id = ""
        final_message_id = ""
        metrics = {}

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()

                if line_str.startswith("data:"):
                    data_str = line_str[len("data:"):].strip()

                    if data_str == "[DONE]":
                        break

                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if event.get("eventType") == "fulfillment":
                        if "answer" in event:
                            full_answer += event["answer"]
                        if "sessionId" in event:
                            final_session_id = event["sessionId"]
                        if "messageId" in event:
                            final_message_id = event["messageId"]
                    elif event.get("eventType") == "metricsLog":
                        if "publicMetrics" in event:
                            metrics = event["publicMetrics"]

        final_response = {
            "message": "Chat query submitted successfully",
            "data": {
                "sessionId": final_session_id,
                "messageId": final_message_id,
                "answer": full_answer,
                "metrics": metrics,
                "status": "completed",
                "contextMetadata": context_metadata,
            },
        }

        formatted = json.dumps(final_response, indent=2)
        print("\n✅ Final Response (with contextMetadata appended):")
        print(formatted)

if __name__ == "__main__":
    main()