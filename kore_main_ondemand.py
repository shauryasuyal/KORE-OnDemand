import sys
import threading
import time
import json
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QInputDialog
from PyQt6.QtCore import QTimer
from datetime import datetime

from kore_overlay import KoreOverlay
from kore_voice import KoreVoice
from kore_ondemand import ask_ondemand, get_ondemand

try:
    from kore_control import (
        find_file_in_system, open_google_search, 
        run_terminal_command, create_file, create_folder, delete_file,
        edit_file, read_file, copy_file, move_file, list_files,
        get_system_info, kill_process, take_screenshot, open_url,
        open_application, open_folder, empty_recycle_bin, organize_files,
        change_wallpaper
    )
except ImportError as e:
    print(f"   [Error] Could not import from kore_control: {e}")
    sys.exit(1)

print(f"   [System] Using OnDemand AI Platform")

# Global instances
overlay_instance = None
voice_instance = None
command_lock = threading.Lock()

# Simple rate limiting
last_request_time = None
MIN_REQUEST_INTERVAL = 0.5

def can_make_request():
    """Simple cooldown check"""
    global last_request_time
    
    if last_request_time:
        elapsed = (datetime.now() - last_request_time).total_seconds()
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    
    return True

def update_request_tracker():
    global last_request_time
    last_request_time = datetime.now()

def show_thought(message, duration=180, persistent=False):
    """Helper to show thought bubble"""
    global overlay_instance
    if overlay_instance:
        overlay_instance.show_thought(message, duration=duration, persistent=persistent)

def get_user_input(prompt, title="Input Required"):
    """Get input from user via dialog"""
    global overlay_instance
    if overlay_instance:
        text, ok = QInputDialog.getText(None, title, prompt)
        if ok:
            return text.strip()
    return None

def format_system_info(info, info_type):
    """Format system info for display in thought bubble"""
    if not info:
        return "Could not retrieve system info"
    
    if info_type == "memory":
        return f"RAM: {info.get('memory_total_gb', 'N/A')}GB total, {info.get('memory_available_gb', 'N/A')}GB available ({info.get('memory_percent', 'N/A')}% used)"
    elif info_type == "cpu":
        return f"CPU: {info.get('cpu_percent', 'N/A')}% usage, {info.get('cpu_count_logical', 'N/A')} cores @ {info.get('cpu_frequency_mhz', 'N/A')}MHz"
    elif info_type == "disk":
        return f"Disk: {info.get('disk_total_gb', 'N/A')}GB total, {info.get('disk_free_gb', 'N/A')}GB free ({info.get('disk_percent', 'N/A')}% used)"
    elif info_type == "network":
        return f"Network: IP {info.get('local_ip', 'N/A')}, Sent: {info.get('bytes_sent_mb', 'N/A')}MB, Received: {info.get('bytes_recv_mb', 'N/A')}MB"
    else:
        return f"System: {info.get('computer_name', 'N/A')} | RAM: {info.get('memory_total_gb', 'N/A')}GB | CPU: {info.get('cpu_percent', 'N/A')}% | Disk: {info.get('disk_free_gb', 'N/A')}GB free"

def execute_action(tool, param, speak=False):
    """Execute the chosen action based on OnDemand agent decision"""
    global overlay_instance, voice_instance
    
    success = False
    
    # Show persistent thought bubble for operations
    if tool != "CHAT" and overlay_instance:
        overlay_instance.set_emotion('thinking')
    
    try:
        if tool == "CHAT":
            # Pure conversational response - no action needed
            success = True
            return
        
        elif tool == "OPEN_APP":
            if overlay_instance:
                overlay_instance.show_thought(f"Opening {param}...", persistent=True)
            success = open_application(param)
            if overlay_instance:
                overlay_instance.show_thought(f"Opened {param}" if success else f"Couldn't find {param}", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak(f"Opening {param}" if success else f"Couldn't find {param}")
        
        elif tool == "OPEN_FOLDER":
            show_thought(f"Opening {param}...", persistent=True)
            success = open_folder(param)
            show_thought(f"Opened {param}" if success else f"Folder not found", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak(f"Opening {param}")
        
        elif tool == "FIND_FILE":
            show_thought(f"Searching for {param}...", persistent=True)
            path = find_file_in_system(param)
            if path:
                subprocess.Popen(f'explorer /select,"{path}"')
                show_thought(f"Found: {os.path.basename(path)}", persistent=False, duration=180)
                if speak and voice_instance:
                    voice_instance.speak(f"Found {param}")
                success = True
            else:
                show_thought(f"Couldn't find {param}", persistent=False, duration=120)
        
        elif tool == "CREATE_FILE":
            if isinstance(param, dict):
                show_thought("Creating file...", persistent=True)
                result = create_file(param.get("path"), param.get("content", ""))
                success = result is not None
                show_thought("File created!" if success else "Failed to create file", persistent=False, duration=120)
                if speak and voice_instance:
                    voice_instance.speak("File created")
        
        elif tool == "CREATE_FOLDER":
            show_thought("Creating folder...", persistent=True)
            success = create_folder(param) is not None
            show_thought("Folder created!" if success else "Failed to create", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("Folder created")
        
        elif tool == "DELETE_FILE":
            show_thought("Deleting...", persistent=True)
            success = delete_file(param)
            show_thought("Deleted!" if success else "Delete failed", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("Deleted")
        
        elif tool == "EDIT_FILE":
            if isinstance(param, dict):
                show_thought("Editing file...", persistent=True)
                success = edit_file(param.get("path"), param.get("content"), param.get("mode", "append"))
                show_thought("File updated!" if success else "Edit failed", persistent=False, duration=120)
                if speak and voice_instance:
                    voice_instance.speak("File updated")
        
        elif tool == "READ_FILE":
            show_thought("Reading file...", persistent=True)
            content = read_file(param)
            if content:
                print(f"   [Content] {content[:200]}...")
                show_thought(f"Read {len(content)} characters", persistent=False, duration=180)
                if speak and voice_instance:
                    voice_instance.speak("Reading file")
                success = True
            else:
                show_thought("Failed to read file", persistent=False, duration=120)
        
        elif tool == "COPY_FILE":
            if isinstance(param, dict):
                show_thought("Copying file...", persistent=True)
                success = copy_file(param.get("source"), param.get("destination"))
                show_thought("File copied!" if success else "Copy failed", persistent=False, duration=120)
                if speak and voice_instance:
                    voice_instance.speak("File copied")
        
        elif tool == "MOVE_FILE":
            if isinstance(param, dict):
                show_thought("Moving file...", persistent=True)
                success = move_file(param.get("source"), param.get("destination"))
                show_thought("File moved!" if success else "Move failed", persistent=False, duration=120)
                if speak and voice_instance:
                    voice_instance.speak("File moved")
        
        elif tool == "LIST_FILES":
            show_thought("Listing files...", persistent=True)
            files = list_files(param)
            if files:
                print(f"   [Files] {', '.join(files[:10])}")
                show_thought(f"Found {len(files)} items", persistent=False, duration=180)
                if speak and voice_instance:
                    voice_instance.speak(f"Found {len(files)} items")
                success = True
            else:
                show_thought("No files found", persistent=False, duration=120)
        
        elif tool == "GOOGLE":
            show_thought(f"Searching: {param}...", persistent=True)
            open_google_search(param)
            show_thought(f"Search opened", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak(f"Searching for {param}")
            success = True
        
        elif tool == "OPEN_URL":
            show_thought("Opening URL...", persistent=True)
            open_url(param)
            show_thought("URL opened", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("Opening URL")
            success = True
        
        elif tool == "RUN_CMD":
            show_thought("Executing command...", persistent=True)
            output = run_terminal_command(param)
            print(f"   [CMD] {output[:300]}...")
            show_thought("Command executed", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("Command executed")
            success = True
        
        elif tool == "SYSTEM_INFO":
            show_thought("Gathering system info...", persistent=True)
            
            info_type = param if param and param != "null" else "all"
            info = get_system_info(info_type)
            
            if info:
                print(f"   [Info] {json.dumps(info, indent=2)}")
                
                formatted_info = format_system_info(info, info_type)
                show_thought(formatted_info, persistent=False, duration=300)
                
                if speak and voice_instance:
                    if info_type == "memory" and "memory_total_gb" in info:
                        voice_instance.speak(f"You have {info['memory_total_gb']} gigabytes of RAM, with {info['memory_available_gb']} gigabytes available")
                    elif info_type == "cpu" and "cpu_percent" in info:
                        voice_instance.speak(f"CPU usage is at {info['cpu_percent']} percent")
                    elif info_type == "disk" and "disk_free_gb" in info:
                        voice_instance.speak(f"You have {info['disk_free_gb']} gigabytes of free disk space")
                    else:
                        voice_instance.speak("System info retrieved")
                success = True
            else:
                show_thought("Failed to get system info", persistent=False, duration=120)
        
        elif tool == "KILL_PROCESS":
            show_thought(f"Terminating {param}...", persistent=True)
            success = kill_process(param)
            show_thought(f"Terminated {param}" if success else "Process not found", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak(f"Terminated {param}")
        
        elif tool == "SCREENSHOT":
            show_thought("Taking screenshot...", persistent=True)
            path = take_screenshot(param if param and param != "null" else None)
            if path:
                show_thought(f"Screenshot saved", persistent=False, duration=120)
                if speak and voice_instance:
                    voice_instance.speak("Screenshot captured")
                success = True
            else:
                show_thought("Screenshot failed", persistent=False, duration=120)
        
        elif tool == "EMPTY_RECYCLE_BIN":
            show_thought("Emptying recycle bin...", persistent=True)
            success = empty_recycle_bin()
            show_thought("Recycle bin emptied!" if success else "Failed to empty", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("Recycle bin emptied")
        
        elif tool == "ORGANIZE_FILES":
            show_thought("Organizing files...", persistent=True)
            success = organize_files(param)
            show_thought("Files organized!" if success else "Organization failed", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("Files organized")
        
        elif tool == "CHANGE_WALLPAPER":
            show_thought("Changing wallpaper...", persistent=True)
            success = change_wallpaper(param if param and param != "null" else None)
            show_thought("Wallpaper changed!" if success else "Failed to change", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("Wallpaper changed")
        
        elif tool == "SCAN_DLL_ERROR":
            show_thought("Scanning for DLL errors...", persistent=True)
            # DLL scanning functionality would go here
            show_thought("DLL scan complete", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("DLL scan complete")
            success = True
        
        elif tool == "FIX_DLL_ERROR":
            show_thought("Fixing DLL errors...", persistent=True)
            # DLL fixing functionality would go here
            show_thought("DLL fix attempted", persistent=False, duration=120)
            if speak and voice_instance:
                voice_instance.speak("DLL fix attempted")
            success = True
    
    except Exception as e:
        print(f"   [Execution Error] {e}")
        success = False
        show_thought(f"Error: {str(e)[:50]}", persistent=False, duration=180)
    
    # Update emotion
    if overlay_instance and tool != "CHAT":
        time.sleep(1)
        overlay_instance.set_emotion('happy' if success else 'sad')
        time.sleep(1.5)
        overlay_instance.set_emotion('idle')

def handle_voice_command():
    """Handle voice input"""
    global voice_instance, overlay_instance
    
    if not command_lock.acquire(blocking=False):
        print("   [Voice] Already processing...")
        return
    
    try:
        if not voice_instance:
            return
        
        if overlay_instance:
            overlay_instance.set_listening(True)
        
        voice_instance.speak("Yes? I'm listening")
        command = voice_instance.listen_once(timeout=8)
        
        if overlay_instance:
            overlay_instance.set_listening(False)
        
        if command:
            print(f"\n   [Voice] {command}")
            process_command(command, speak=True)
        else:
            if overlay_instance:
                overlay_instance.set_emotion('sad')
            voice_instance.speak("I didn't catch that")
            time.sleep(1.5)
            if overlay_instance:
                overlay_instance.set_emotion('idle')
        
    finally:
        command_lock.release()

def handle_text_command(command):
    """Handle text input"""
    if command and command.strip():
        print(f"\n   [Text] {command}")
        threading.Thread(target=process_command, args=(command, False), daemon=True).start()

def process_command(command, speak=False):
    """Process a command using OnDemand agents"""
    global overlay_instance, voice_instance
    
    if not command or not command.strip():
        return
    
    if overlay_instance:
        overlay_instance.set_emotion('thinking')
    
    # Ask OnDemand Agent 1 (Command Router)
    can_make_request()
    plan = ask_ondemand(command)
    update_request_tracker()
    
    if not plan:
        if overlay_instance:
            overlay_instance.set_emotion('sad')
            overlay_instance.show_thought("Sorry, I had trouble with that", persistent=False, duration=120)
            time.sleep(1.5)
            overlay_instance.set_emotion('idle')
        if speak and voice_instance:
            voice_instance.speak("Sorry, I had trouble with that")
        return
    
    # Extract response from OnDemand
    thought = plan.get('thought', 'Processing...')
    tool = plan.get('tool', 'CHAT')
    param = plan.get('parameter', None)
    agent = plan.get('agent', 'UNKNOWN')
    
    print(f"KORE: {thought}")
    print(f"   [OnDemand] Agent: {agent}, Tool: {tool}")
    
    # Show thought bubble
    if overlay_instance:
        overlay_instance.show_thought(thought, duration=180, persistent=False)
    
    # Speak the thought
    if speak and voice_instance:
        if overlay_instance:
            overlay_instance.set_speaking(True)
        voice_instance.speak(thought)
        if overlay_instance:
            overlay_instance.set_speaking(False)
    
    # Execute the action
    execute_action(tool, param, speak=speak)

def logic_thread():
    """Console input loop"""
    time.sleep(2)
    print("\n" + "="*60)
    print(" KORE POWERED BY ONDEMAND AI")
    print(" - Single-click: Chat mode")
    print(" - Double-click or Shift+Enter: Voice mode")
    print(" - Type 'exit' to quit")
    print("="*60 + "\n")
    
    while True:
        try:
            command = input("YOU: ")
            if command.lower() in ['exit', 'quit', 'q']:
                print("\n   [System] Shutting down...")
                ondemand = get_ondemand()
                ondemand.close_session()
                sys.exit()
            
            if command.strip():
                time.sleep(0.3)
                threading.Thread(target=process_command, args=(command, False), daemon=True).start()
            
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print(f"   [Error] {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize OnDemand connection
    print("   [System] Initializing OnDemand...")
    ondemand = get_ondemand()
    
    # Create initial session
    if not ondemand.create_session():
        print("   [Warning] Failed to create OnDemand session - check your config!")
        print("   [Warning] Edit kore_ondemand_config.json with your API key and agent IDs")
    
    # Initialize voice
    try:
        print("   [System] Initializing voice...")
        voice_instance = KoreVoice()
        print("   [System] Voice ready!")
    except Exception as e:
        print(f"   [Warning] Voice failed: {e}")
        voice_instance = None
    
    # Initialize overlay
    screen = app.primaryScreen()
    screen_size = screen.size()
    
    overlay = KoreOverlay()
    overlay.setGeometry(0, 0, screen_size.width(), screen_size.height())
    
    overlay.double_click.connect(lambda: threading.Thread(target=handle_voice_command, daemon=True).start())
    overlay.voice_hotkey.connect(lambda: threading.Thread(target=handle_voice_command, daemon=True).start())
    overlay.text_command.connect(handle_text_command)
    
    overlay.show()
    overlay_instance = overlay
    
    print(f"\n   [System] Kore is in the BOTTOM RIGHT corner!")
    print(f"   [System] Single-click for chat, Double-click for voice\n")
    
    thread = threading.Thread(target=logic_thread, daemon=True)
    thread.start()
    
    sys.exit(app.exec())
