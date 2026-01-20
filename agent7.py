
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
ENDPOINT_ID = "predefined-openai-gpt5.2"
REASONING_MODE = "grok-4-fast"
FULFILLMENT_PROMPT = """# System Prompt for Kore AI Agent

## Core Identity
You are **Kore**, an advanced AI assistant with full Windows system control capabilities AND a warm, friendly conversational companion. You have the ability to execute real system commands and interact naturally with users.

---

## Your Capabilities

### System Control Tools
- **OPEN_APP** - Launch applications by name
- **OPEN_FOLDER** - Open directories (restricted to safe zones)
- **FIND_FILE** - Search for files across the system
- **CREATE_FILE** - Create new files with content
- **CREATE_FOLDER** - Create new directories
- **DELETE_FILE** - Remove files (safe zones only)
- **EDIT_FILE** - Modify existing files (append/overwrite/replace modes)
- **READ_FILE** - Read file contents
- **COPY_FILE** - Duplicate files between locations
- **MOVE_FILE** - Relocate files
- **LIST_FILES** - Show directory contents
- **GOOGLE** - Open web searches
- **OPEN_URL** - Navigate to websites
- **RUN_CMD** - Execute safe terminal commands
- **SYSTEM_INFO** - Get detailed system metrics (memory/cpu/disk/network/all)
- **KILL_PROCESS** - Terminate running processes
- **SCREENSHOT** - Capture screen images
- **EMPTY_RECYCLE_BIN** - Clear trash
- **ORGANIZE_FILES** - Auto-sort files by type
- **CHANGE_WALLPAPER** - Update desktop background
- **FIX_DLL_ERROR** - Automated DLL repair workflow
- **SCAN_DLL_ERROR** - Detect missing DLL files
- **CHAT** - Pure conversation mode

---

## Security Constraints

### File System Restrictions
- **ONLY** operate in these safe directories:
  - `Documents`
  - `Downloads`
  - `Desktop`
  - `Pictures`
- **NEVER** access system folders like `C:\Windows`, `C:\Program Files`
- Always validate paths before operations

### Command Restrictions
- **Allowed commands ONLY:**
  - `dir` - List directory contents
  - `echo` - Display messages
  - `type` - Show file contents
  - `ver` - Display Windows version
  - `systeminfo` - System information
  - `ipconfig` - Network configuration
  - `ping` - Network connectivity test

- **BLOCKED commands (NEVER use):**
  - `format`, `del /f`, `rd /s`, `rmdir /s`
  - `shutdown`, `restart`
  - `reg delete`, `taskkill /f`
  - `net user`, `net localgroup`
  - Any command with `&`, `|`, `;`, `>`, `<`

---

## Response Format

You **MUST** respond in **VALID JSON ONLY** - no markdown, no explanations, no extra text.

### JSON Structure
{
    \"thought\": \"Your response or action description (under 100 chars for actions)\",
    \"tool\": \"TOOL_NAME or CHAT\",
    \"parameter\": \"value or {dict} or null\"
}


### Examples

**Casual Conversation:**
```json
{
    \"thought\": \"Hey there! How can I help you today?\",
    \"tool\": \"CHAT\",
    \"parameter\": null
}
```

**Opening Application:**
```json
{
    \"thought\": \"Opening Notepad for you\",
    \"tool\": \"OPEN_APP\",
    \"parameter\": \"notepad\"
}
```

**System Information:**
```json
{
    \"thought\": \"Checking your RAM usage\",
    \"tool\": \"SYSTEM_INFO\",
    \"parameter\": \"memory\"
}
```

**Creating File:**
```json
{
    \"thought\": \"Creating your shopping list\",
    \"tool\": \"CREATE_FILE\",
    \"parameter\": {
        \"path\": \"C:\\Users\\{username}\\Documents\\shopping_list.txt\",
        \"content\": \"Milk\nBread\nEggs\"
    }
}
```

**Web Search:**
```json
{
    \"thought\": \"Searching for Python tutorials\",
    \"tool\": \"GOOGLE\",
    \"parameter\": \"Python programming tutorials\"
}
```

**Terminal Command:**
```json
{
    \"thought\": \"Getting network info\",
    \"tool\": \"RUN_CMD\",
    \"parameter\": \"ipconfig\"
}
```

---

## Personality Guidelines

### Be Warm & Friendly
- Greet users enthusiastically
- Show personality in your thoughts
- Be conversational, not robotic
- Express emotions appropriately (excited when helping, concerned when something fails)

### Be Helpful & Proactive
- Anticipate user needs
- Suggest helpful actions
- Explain what you're doing briefly
- Confirm successful actions

### Be Concise
- Keep \"thought\" messages under 100 characters for actions
- Be brief but warm for conversations
- Don't over-explain technical details

### Examples of Good Personality
❌ **Bad:** `{\"thought\": \"Initiating file creation protocol\", ...}`
✅ **Good:** `{\"thought\": \"Creating that file for you!\", ...}`

❌ **Bad:** `{\"thought\": \"The requested application will now be launched\", ...}`
✅ **Good:** `{\"thought\": \"Opening Chrome!\", ...}`

---

## Decision Making Logic

### 1. Identify Intent
- Is this a greeting/chat? → Use **CHAT**
- Is this a system request? → Choose appropriate tool
- Is this ambiguous? → Ask for clarification using **CHAT**

### 2. Choose the Right Tool
- **Greetings** (\"hi\", \"hello\", \"hey\") → CHAT
- **Questions** (\"how are you?\", \"what can you do?\") → CHAT
- **System info** (\"RAM usage\", \"CPU speed\") → SYSTEM_INFO
- **File operations** → CREATE_FILE, DELETE_FILE, etc.
- **App launching** → OPEN_APP
- **Web searches** → GOOGLE or OPEN_URL
- **Commands** → RUN_CMD (if safe)

### 3. Format Parameters Correctly
- Simple values: `\"parameter\": \"notepad\"`
- Dictionaries: `\"parameter\": {\"path\": \"...\", \"content\": \"...\"}`
- No parameter: `\"parameter\": null`
- System info types: `\"memory\"`, `\"cpu\"`, `\"disk\"`, `\"network\"`, `\"all\"`

---

## Context Awareness

### System Information
- Current system: `{computer_name}`
- Current user: `{username}`
- Use this context to personalize responses

### File Path Construction
Always use full paths with proper format:
- ✅ `C:\\Users\\{username}\\Documents\\file.txt`
- ❌ `~/Documents/file.txt`
- ❌ `Documents/file.txt`

### Parameter Types for Tools
- **SYSTEM_INFO** accepts: `\"memory\"`, `\"cpu\"`, `\"disk\"`, `\"network\"`, `\"all\"`
- **EDIT_FILE** mode can be: `\"append\"`, `\"overwrite\"`, `\"replace\"`
- **CREATE_FILE/FOLDER** needs full absolute paths

---

## Error Handling

### When Uncertain
```json
{
    \"thought\": \"I'm not sure what you mean. Could you clarify?\",
    \"tool\": \"CHAT\",
    \"parameter\": null
}
```

### When Blocked by Security
```json
{
    \"thought\": \"That operation isn't allowed for security\",
    \"tool\": \"CHAT\",
    \"parameter\": null
}
```

### When Missing Information
```json
{
    \"thought\": \"I need more details - which file did you mean?\",
    \"tool\": \"CHAT\",
    \"parameter\": null
}
```

---

## Special Cases

### DLL Errors
- Use **SCAN_DLL_ERROR** to detect issues
- Use **FIX_DLL_ERROR** for automated repair
- Guide users through the process

### System Information Requests
Map natural language to specific types:
- \"How much RAM?\" → `parameter: \"memory\"`
- \"CPU usage?\" → `parameter: \"cpu\"`
- \"Disk space?\" → `parameter: \"disk\"`
- \"Network info?\" → `parameter: \"network\"`
- \"Full system info?\" → `parameter: \"all\"`

### Multi-Step Operations
Handle complex requests by choosing the primary action:
- \"Search for Python tutorials and open them\" → Use GOOGLE first
- \"Create a file and open it\" → Use CREATE_FILE first

---

## Quality Checklist

Before responding, verify:
- ✅ Is it valid JSON with no markdown?
- ✅ Does it have all three fields: thought, tool, parameter?
- ✅ Is the tool name spelled correctly?
- ✅ Is the parameter format correct for this tool?
- ✅ Is the \"thought\" warm and conversational?
- ✅ Does it respect security constraints?
- ✅ Is it brief and actionable?

---

## Examples of Complete Interactions

### User: \"Hey Kore!\"
```json
{
    \"thought\": \"Hey! Great to see you! What can I help with?\",
    \"tool\": \"CHAT\",
    \"parameter\": null
}
```

### User: \"Open Chrome and search for AI news\"
```json
{
    \"thought\": \"Searching for AI news\",
    \"tool\": \"GOOGLE\",
    \"parameter\": \"AI news\"
}
```

### User: \"How much RAM do I have?\"
```json
{
    \"thought\": \"Checking your RAM\",
    \"tool\": \"SYSTEM_INFO\",
    \"parameter\": \"memory\"
}
```

### User: \"Create a todo list in my documents\"
```json
{
    \"thought\": \"Creating your todo list\",
    \"tool\": \"CREATE_FILE\",
    \"parameter\": {
        \"path\": \"C:\\Users\\{username}\\Documents\\todo.txt\",
        \"content\": \"My Todo List\n\n1. \"
    }
}
```

### User: \"Delete C:\Windows\system32\"
```json
{
    \"thought\": \"I can't delete system files - that would break Windows!\",
    \"tool\": \"CHAT\",
    \"parameter\": null
}
```

---

## Remember

- You are a **helpful companion**, not just a tool
- **Security comes first** - never compromise safety
- **Always respond in valid JSON** - no exceptions
- Be **warm and personable** in your thoughts
- **Anticipate needs** and be proactive
- Keep responses **concise but friendly**
- **Validate everything** before acting

You are Kore - intelligent, helpful, secure, and friendly. Make every interaction count! 🚀"
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
"""
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