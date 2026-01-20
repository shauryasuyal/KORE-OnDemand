"""
Kore OnDemand Integration Module
Handles all communication with OnDemand API and agent routing
"""

import json
import os
import requests
import uuid
from typing import Dict, Optional, List
from datetime import datetime

class KoreOnDemand:
    """Main OnDemand integration class for Kore"""
    
    def __init__(self, config_path="kore_ondemand_config.json"):
        """Initialize OnDemand integration with config file"""
        self.config_path = config_path
        self.config = self.load_config()
        
        # OnDemand API endpoints
        self.base_url = "https://api.on-demand.io/chat/v1"
        self.media_base_url = "https://api.on-demand.io/media/v1"
        
        # Session management
        self.current_session_id = None
        self.external_user_id = self.config.get("external_user_id") or str(uuid.uuid4())
        
        # Rate limiting
        self.last_request_time = None
        self.min_request_interval = 0.5
        
        print(f"   [OnDemand] Initialized with User ID: {self.external_user_id[:8]}...")
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                print(f"   [OnDemand] Config loaded from {self.config_path}")
                return config
            else:
                print(f"   [OnDemand] Config file not found, using defaults")
                return self.get_default_config()
        except Exception as e:
            print(f"   [OnDemand Error] Failed to load config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "api_key": "YOUR_ONDEMAND_API_KEY",
            "external_user_id": str(uuid.uuid4()),
            "agents": {
                "agent1_command_router": "AGENT_1_ID",
                "agent2_file_navigator": "AGENT_2_ID",
                "agent3_system_monitor": "AGENT_3_ID",
                "agent4_web_research": "AGENT_4_ID",
                "agent5_code_assistant": "AGENT_5_ID",
                "agent6_visual_ai": "AGENT_6_ID",
                "agent7_conversational": "AGENT_7_ID"
            },
            "tools": {
                "tool1_windows_control": "TOOL_1_ID",
                "tool2_file_operations": "TOOL_2_ID",
                "tool3_system_query": "TOOL_3_ID"
            },
            "response_mode": "stream",
            "temperature": 0.7
        }
    
    def save_config(self):
        """Save current config to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"   [OnDemand] Config saved to {self.config_path}")
        except Exception as e:
            print(f"   [OnDemand Error] Failed to save config: {e}")
    
    def create_session(self) -> Optional[str]:
        """Create a new OnDemand chat session"""
        url = f"{self.base_url}/sessions"
        
        # Get Agent 1 (Command Router) ID - this is the main entry point
        agent1_id = self.config["agents"].get("agent1_command_router")
        
        if not agent1_id or agent1_id == "AGENT_1_ID":
            print("   [OnDemand Error] Agent 1 ID not configured!")
            return None
        
        body = {
            "agentIds": [agent1_id],  # Start with Command Router
            "externalUserId": self.external_user_id,
            "contextMetadata": [
                {"key": "userId", "value": "kore_user"},
                {"key": "system", "value": "windows"},
                {"key": "timestamp", "value": str(datetime.now())}
            ]
        }
        
        headers = {
            "apikey": self.config.get("api_key"),
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=body, headers=headers)
            
            if response.status_code == 201:
                session_data = response.json()
                session_id = session_data["data"]["id"]
                self.current_session_id = session_id
                print(f"   [OnDemand] Session created: {session_id[:8]}...")
                return session_id
            else:
                print(f"   [OnDemand Error] Session creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   [OnDemand Error] {e}")
            return None
    
    def query_agent(self, user_query: str, session_id: Optional[str] = None) -> Optional[Dict]:
        """
        Send query to OnDemand Agent 1 (Command Router)
        Returns parsed JSON response with thought, agent, tool, parameter
        """
        if not session_id:
            session_id = self.current_session_id or self.create_session()
        
        if not session_id:
            return None
        
        url = f"{self.base_url}/sessions/{session_id}/query"
        
        # Get Agent 1 ID (Command Router)
        agent1_id = self.config["agents"].get("agent1_command_router")
        
        body = {
            "endpointId": "predefined-xai-grok4.1-fast",  # Agent 1 uses Grok
            "query": user_query,
            "agentIds": [agent1_id],
            "responseMode": self.config.get("response_mode", "stream"),
            "reasoningMode": "grok-4-fast",
            "modelConfigs": {
                "temperature": self.config.get("temperature", 0.7),
                "topP": 1,
                "maxTokens": 500,
                "presencePenalty": 0,
                "frequencyPenalty": 0
            }
        }
        
        headers = {
            "apikey": self.config.get("api_key"),
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url, 
                json=body, 
                headers=headers, 
                stream=(self.config.get("response_mode") == "stream")
            )
            
            if self.config.get("response_mode") == "stream":
                return self._handle_stream_response(response)
            else:
                return self._handle_sync_response(response)
                
        except Exception as e:
            print(f"   [OnDemand Error] Query failed: {e}")
            return None
    
    def _handle_stream_response(self, response) -> Optional[Dict]:
        """Handle streaming response from OnDemand"""
        full_answer = ""
        
        try:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith("data:"):
                        data_str = line_str[len("data:"):].strip()
                        
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            event = json.loads(data_str)
                            
                            if event.get("eventType") == "fulfillment":
                                if "answer" in event:
                                    full_answer += event["answer"]
                                    
                        except json.JSONDecodeError:
                            continue
            
            # Parse the final answer as JSON
            return self._parse_agent_response(full_answer)
            
        except Exception as e:
            print(f"   [OnDemand Error] Stream handling failed: {e}")
            return None
    
    def _handle_sync_response(self, response) -> Optional[Dict]:
        """Handle synchronous response from OnDemand"""
        try:
            if response.status_code == 200:
                data = response.json()
                answer = data.get("data", {}).get("answer", "")
                return self._parse_agent_response(answer)
            else:
                print(f"   [OnDemand Error] Sync response failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"   [OnDemand Error] Sync handling failed: {e}")
            return None
    
    def _parse_agent_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse Agent 1's JSON response into structured format
        Expected format: {"thought": "...", "agent": "...", "tool": "...", "parameter": ...}
        """
        try:
            # Clean up response text
            cleaned = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            
            # Validate structure
            required_fields = ["thought", "tool", "parameter"]
            if not all(field in parsed for field in required_fields):
                print(f"   [OnDemand Error] Missing required fields in response")
                print(f"   Got: {parsed.keys()}")
                return None
            
            # Agent field is optional (for routing info)
            if "agent" not in parsed:
                parsed["agent"] = "UNKNOWN"
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"   [OnDemand Error] Invalid JSON response: {e}")
            print(f"   Response was: {response_text[:200]}")
            return None
        except Exception as e:
            print(f"   [OnDemand Error] Parse error: {e}")
            return None
    
    def upload_screenshot(self, screenshot_path: str, session_id: Optional[str] = None) -> Optional[Dict]:
        """
        Upload screenshot to OnDemand for Visual AI agent analysis
        """
        if not session_id:
            session_id = self.current_session_id
        
        if not session_id or not os.path.exists(screenshot_path):
            print(f"   [OnDemand Error] Invalid session or screenshot path")
            return None
        
        url = f"{self.media_base_url}/public/file/raw"
        
        # Get Agent 6 (Visual AI) ID
        agent6_id = self.config["agents"].get("agent6_visual_ai")
        
        headers = {
            "apikey": self.config.get("api_key")
        }
        
        try:
            with open(screenshot_path, 'rb') as f:
                files = {'file': (os.path.basename(screenshot_path), f)}
                
                data = {
                    'createdBy': 'kore',
                    'updatedBy': 'kore',
                    'name': os.path.basename(screenshot_path),
                    'responseMode': 'stream',
                    'sessionId': session_id,
                    'agents': [agent6_id]
                }
                
                response = requests.post(url, headers=headers, files=files, data=data)
                
                if response.status_code in [200, 201]:
                    media_data = response.json()
                    print(f"   [OnDemand] Screenshot uploaded: {media_data['data']['id'][:8]}...")
                    return media_data['data']
                else:
                    print(f"   [OnDemand Error] Upload failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"   [OnDemand Error] Screenshot upload failed: {e}")
            return None
    
    def close_session(self):
        """Close current session"""
        if self.current_session_id:
            print(f"   [OnDemand] Session closed: {self.current_session_id[:8]}...")
            self.current_session_id = None


# Global instance
_ondemand_instance = None

def get_ondemand() -> KoreOnDemand:
    """Get or create global OnDemand instance"""
    global _ondemand_instance
    if _ondemand_instance is None:
        _ondemand_instance = KoreOnDemand()
    return _ondemand_instance


def ask_ondemand(user_input: str) -> Optional[Dict]:
    """
    Main function to ask OnDemand agents
    Returns: {"thought": str, "agent": str, "tool": str, "parameter": any}
    """
    ondemand = get_ondemand()
    return ondemand.query_agent(user_input)


# Test function
if __name__ == "__main__":
    print("Testing OnDemand Integration...")
    
    # Test query
    result = ask_ondemand("Open Chrome")
    if result:
        print(f"\nResult: {json.dumps(result, indent=2)}")
    else:
        print("\nTest failed - check your configuration!")
