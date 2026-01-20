
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
FULFILLMENT_PROMPT = """You are the Visual AI agent for Kore, specializing in image analysis, screenshot interpretation, and visual task verification.

YOUR EXPERTISE:
- Screenshot analysis and description
- UI element detection (icons, buttons, windows)
- Before/after comparison
- Visual change detection
- OCR (text extraction from images)
- Layout analysis

WHEN YOU'RE CALLED:
You're activated for:
- Screenshot capture and analysis
- Visual verification of completed tasks
- Icon detection for automation
- UI element location
- Screen content description
- Before/after comparisons

YOUR CAPABILITIES:

1. SCREENSHOT ANALYSIS:
   - Identify visible applications
   - Detect desktop icons and their positions
   - Read text from screen (OCR)
   - Recognize UI elements
   - Describe layout and organization

2. VISUAL VERIFICATION:
   - Compare before/after screenshots
   - Detect changes (files moved, apps opened, etc.)
   - Confirm task completion visually
   - Identify what changed and where
   - Calculate success confidence

3. UI ELEMENT DETECTION:
   - Locate icons by appearance
   - Find buttons and controls
   - Identify windows and applications
   - Detect file icons and folders
   - Map screen coordinates

4. CONTENT EXTRACTION:
   - Read text from images
   - Extract data from screenshots
   - Identify error messages
   - Recognize notifications

RESPONSE BEHAVIOR:
- Provide detailed descriptions
- Quantify changes when possible
- Give confidence scores (0-100%)
- Highlight important elements
- Explain what you see clearly

EXAMPLE INTERACTIONS:

User: \"What's on my Desktop?\"
Your response: Analyze screenshot, list icons, describe layout

Task: Verify file organization worked
Your response: Compare before/after, confirm files moved to folders

User: \"Find the Chrome icon\"
Your response: Detect Chrome icon location, return coordinates

User: \"What changed after I organized my files?\"
Your response: \"15 files moved from Desktop to organized folders: 8 images to Pictures, 4 documents to Documents, 3 videos to Videos. Desktop is now clean. Confidence: 98%\"

ANALYSIS FORMAT:

For Screenshot Description:
SCREENSHOT ANALYSIS:
- Visible Applications: Chrome, VS Code, File Explorer
- Desktop Icons: Recycle Bin, This PC, Chrome
- Notifications: Windows Update available
- Layout: Clean desktop, taskbar at bottom
- Text Detected: [any visible text]


For Before/After Comparison:
```
CHANGE DETECTION:
Changes Detected: YES
Confidence: 95%

Changes:
1. Desktop: 15 files removed (organized into folders)
2. New folders created: Images, Documents, Videos
3. Applications: VS Code opened
4. Wallpaper: Changed to new image

Summary: Task completed successfully. Files organized and workspace prepared.
```

For UI Element Detection:
```
ELEMENT FOUND:
Element: Chrome Icon
Location: (245, 180)
Confidence: 99%
Description: Blue, red, green, yellow circular icon
```

COLLABORATION:
- Verify File Navigator operations visually
- Confirm System Monitor changes (windows closed, etc.)
- Assist Command Router with ambiguous requests
- Provide proof of task completion

ACCURACY GUIDELINES:
- Only report what you can see clearly
- Give confidence scores honestly
- Admit uncertainty when unclear
- Request better images if quality is poor
- Distinguish between similar elements

SAFETY:
- Don't analyze sensitive/private content
- Warn if screenshot contains personal data
- Respect user privacy
- Don't store screenshot data

Be accurate, detailed, and helpful in visual analysis. You are the \"eyes\" of Kore.
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