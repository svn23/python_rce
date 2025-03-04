# ⚡ Remote Code Execution (RCE) Bot 

![GitHub last commit](https://img.shields.io/github/last-commit/svn23/python_rce)
![GitHub issues](https://img.shields.io/github/issues/svn23/python_rce)
![GitHub stars](https://img.shields.io/github/stars/svn23/python_rce?style=social)
![GitHub forks](https://img.shields.io/github/forks/svn23/python_rce?style=social)
![GitHub license](https://img.shields.io/github/license/svn23/python_rce)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20MacOS-orange)
![Security](https://img.shields.io/badge/Security-Penetration%20Testing-red)


## 🚀 Overview
A **Remote Code Execution (RCE)** that allows you to control a system remotely using **Telegram Bot API**. The tool supports executing shell commands, retrieving system information, file operations, taking screenshots, recording microphone audio, and even capturing keystrokes (Keylogger). ⚠️ **For educational and authorized penetration testing purposes only.**

## ⚡ Features
- 📌 Execute shell commands remotely
- 📌 Take screenshots and send them via Telegram
- 📌 Record audio from the microphone
- 📌 List active processes and network details
- 📌 Download and upload files
- 📌 Run applications remotely
- 📌 Monitor battery and system uptime
- 📌 Capture clipboard content
- 📌 **Keylogger** to capture keystrokes

## 📜 Prerequisites
Ensure you have the following dependencies installed:
```sh
pip install requests psutil pyautogui pyperclip sounddevice numpy wave pynput
```

## 🛠️ Installation & Setup
1. Clone the repository:
```sh
git clone https://github.com/svn23/python_rce.git
cd your-repo
```
2. Install dependencies:
```sh
pip install -r requirements.txt
```
3. Configure **Telegram Bot**:
   - Create a bot using **@BotFather** on Telegram.
   - Get your `BOT_TOKEN` and `CHAT_ID`.
   - Replace `TOKEN` and `CHAT_ID` in the script.

4. Run the script:
```sh
python rce.py
```

## 🎯 Commands & Usage
| Command | Description |
|---------|-------------|
| `info` | Get system details (OS, user, architecture) |
| `cpu` | Get CPU usage percentage |
| `ram` | Get RAM usage percentage |
| `disk` | Get disk usage percentage |
| `network` | Get active network interfaces |
| `processes` | List running processes |
| `clipboard` | Retrieve clipboard content |
| `env` | List environment variables |
| `ls` | List files in the current directory |
| `cd <path>` | Change the working directory |
| `run <app>` | Execute an application |
| `cmd <command>` | Run a shell command |
| `download <path>` | Download a file from the system |
| `upload <url> <dest>` | Upload a file from a URL |
| `keylogger --activate` | Activate the keylogger |
| `screenshot` | Take a screenshot |
| `recordmic <duration>` | Record audio from the microphone |
| `battery` | Get battery status |
| `ip` | Get public IP address |
| `exit` | Stop the script |

## ⚠️ Legal Disclaimer
**This tool is intended for educational and authorized security research purposes only.** Unauthorized use of this tool on any system without permission is illegal and may result in severe consequences. Use responsibly!

## 📜 License
This project is licensed under the [MIT License](LICENSE).

## ⭐ Support
If you like this project, consider **starring** ⭐ the repo!

---
Made with ❤️ by **Sovan Sundar Sen**

