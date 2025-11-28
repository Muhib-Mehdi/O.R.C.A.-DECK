
import os
import sys
import json
import time
import ctypes
import threading
import subprocess
import webbrowser

import serial
import pyautogui
import pyperclip
from flask import Flask, jsonify, redirect, render_template_string


PORT = "COM3"
BAUD = 115200
SERIAL_TIMEOUT = 1

AUTO_LOCK_MINUTES = 15

APPS_FILE = "apps.json"
PASSWORDS_FILE = "passwords.json"
LOG_FILE = "orca_access.log"


KEY_TO_NAME = {
    "A": "steam",
    "B": "discord",
    "C": "valorant",
    "D": "youtube",
    "3": "github",
    "6": "infinite",
    "9": "muhib24",
    "#": "brave",
    "2": "instagram",
    "5": "linkedin",
    "8": "other",
    "0": "back"
}


app = Flask(__name__)

system_status = {
    "connected": False,
    "locked": True,
    "decrypted": False,
    "last_unlock": "Never",
    "logs": []
}


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}

    except Exception as e:
        append_log(f"Error loading {path}: {e}")
        return {}


def append_log(entry):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {entry}"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

    system_status["logs"].append({"time": ts.split()[1], "event": entry})

    if len(system_status["logs"]) > 50:
        system_status["logs"].pop(0)


def get_idle_seconds():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)

    try:
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            return millis / 1000.0
    except Exception:
        pass

    return 0


def open_target(target):
    target = os.path.expandvars(target).strip()

    try:
        if target.startswith(("http://", "https://")):
            webbrowser.open(target)

        elif os.path.isdir(target):
            subprocess.Popen(["explorer", target])

        elif sys.platform.startswith("win") and os.path.exists(target):
            os.startfile(target)

        else:
            subprocess.Popen(target, shell=True)

    except Exception as e:
        append_log(f"Launch failed: {e}")




class ORCA:
    def __init__(self):
        self.apps = load_json(APPS_FILE)
        self.passwords = {}
        self.ser = None
        self._stop = False

        threading.Thread(target=self.serial_thread, daemon=True).start()
        threading.Thread(target=self.auto_lock_checker, daemon=True).start()

    def load_passwords(self):
        self.passwords = load_json(PASSWORDS_FILE)
        system_status["decrypted"] = bool(self.passwords)
        append_log("Passwords loaded" if system_status["decrypted"] else "Passwords empty")

    def clear_passwords(self):
        self.passwords = {}
        system_status["decrypted"] = False
        append_log("Passwords cleared from memory")

    def serial_thread(self):
        global system_status

        while not self._stop:
            try:
                self.ser = serial.Serial(PORT, BAUD, timeout=SERIAL_TIMEOUT)
                system_status["connected"] = True
                append_log(f"Serial connected on {PORT}")

                while True:
                    raw = self.ser.readline().decode(errors="ignore").strip()
                    if not raw:
                        continue

                    print("<<", raw)  # Debug output

                    if raw.startswith("APP_LAUNCH:"):
                        key = raw.split(":", 1)[1].strip()
                        if key in self.apps:
                            open_target(self.apps[key])
                            append_log(f"APP_LAUNCH: {key}")
                        else:
                            append_log(f"Unknown APP key: {key}")

                    elif raw.startswith("PASS_LAUNCH:"):
                        self.handle_password_launch(raw)

                    elif raw == "RFID_UNLOCK_OK":
                        system_status["locked"] = False
                        system_status["last_unlock"] = time.strftime("%H:%M:%S")
                        append_log("RFID_UNLOCK_OK — Unlocked")
                        self.load_passwords()

                    elif raw == "RFID_UNLOCK_FAIL":
                        append_log("RFID_UNLOCK_FAIL")

                    else:
                        append_log(f"SERIAL: {raw}")

            except Exception as e:
                system_status["connected"] = False
                append_log(f"Serial error: {e} — retrying")
                time.sleep(2)

    def handle_password_launch(self, raw):
        raw_key = raw.split(":", 1)[1].strip()
        friendly = KEY_TO_NAME.get(raw_key)

        if not friendly or friendly == "back":
            append_log(f"Invalid PASS key: {raw_key}")
            return

        if system_status["locked"]:
            append_log(f"PASS blocked (locked): {friendly}")
            return

        if not system_status["decrypted"]:
            self.load_passwords()
            if not system_status["decrypted"]:
                append_log(f"No credentials for: {friendly}")
                return

        creds = self.passwords.get(friendly)

        if not creds:
            append_log(f"Missing creds: {friendly}")
            return

        if isinstance(creds, str):
            username = ""
            password = creds
        else:
            username = creds.get("username", "")
            password = creds.get("password", "")

        append_log(f"Typing credentials for {friendly}")

        time.sleep(0.6)

        try:
            if username:
                pyautogui.typewrite(username, interval=0.02)
                pyautogui.press("tab")
                time.sleep(0.15)

            if password:
                pyperclip.copy(password)
                pyautogui.typewrite(password, interval=0.02)
                pyautogui.press("enter")

        except Exception as e:
            append_log(f"Typing error: {e}")

    def auto_lock_checker(self):
        while True:
            try:
                if (
                    not system_status["locked"]
                    and get_idle_seconds() >= AUTO_LOCK_MINUTES * 60
                ):
                    system_status["locked"] = True
                    append_log("Auto-locked due to inactivity")
                    self.clear_passwords()
                time.sleep(5)
            except Exception:
                time.sleep(5)


orca = ORCA()


@app.route("/")
def dashboard():
    return render_template_string(dashboard_html, data=system_status)


@app.route("/api/status")
def api_status():
    return jsonify(system_status)


@app.route("/lock")
def lock():
    system_status["locked"] = True
    system_status["decrypted"] = False
    system_status["last_unlock"] = system_status["last_unlock"]
    orca.clear_passwords()
    append_log("Manual lock")
    return redirect("/")


@app.route("/refresh")
def refresh():
    return redirect("/")


if __name__ == "__main__":
    threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0", port=5000, debug=False, use_reloader=False
        ),
        daemon=True,
    ).start()

    print("🌐 Dashboard running at http://127.0.0.1:5000")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        orca._stop = True
        sys.exit(0)
