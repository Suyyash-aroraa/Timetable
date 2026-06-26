import json
import os
import atexit
import time
import subprocess
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from pyngrok import ngrok, conf

# Use local ngrok binary
conf.get_default().ngrok_path = r"C:\ngrok\ngrok.exe"

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, ngrok-skip-browser-warning"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


@app.route("/status", methods=["GET", "OPTIONS"])
def status():
    if request.method == "OPTIONS":
        return "", 200
    data = load_status()
    return jsonify(data)

NGROK_DOMAIN = "unwomanly-shame-pastime.ngrok-free.dev"
NGROK_PORT = 3333

STATUS_FILE = "status.json"

SCHEDULE = [
    {"name": "Gym", "time": "7:00 AM", "skip_weekend": True},
    {"name": "Shake", "time": "9:00 AM", "skip_weekend": True},
    {"name": "Free block", "time": "10:00 AM", "skip_weekend": True},
    {"name": "Kwality", "time": "12:00 PM", "skip_weekend": False},
    {"name": "IELTS", "time": "12:30 PM", "skip_weekend": False},
    {"name": "Game", "time": "2:00 PM", "skip_weekend": False},
    {"name": "GRE", "time": "3:15 PM", "skip_weekend": False},
    {"name": "Lunch / Kwality", "time": "4:00 PM", "skip_weekend": False},
    {"name": "Violin", "time": "6:00 PM", "skip_weekend": False},
    {"name": "Skill building", "time": "8:00 PM", "skip_weekend": False},
    {"name": "Game", "time": "9:00 PM", "skip_weekend": False},
    {"name": "Dinner", "time": "10:30 PM", "skip_weekend": False},
]

STATUS_ORDER = ["upcoming", "current", "done", "skipped"]


def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return default_status()


def default_status():
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "date": today,
        "tasks": [{"name": item["name"], "time": item["time"], "status": "upcoming"} for item in SCHEDULE],
        "globalStatus": "Available",
        "note": "",
        "lastUpdated": datetime.now().isoformat(),
        "ngrokUrl": "",
    }


def save_status(data):
    data["lastUpdated"] = datetime.now().isoformat()
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    # Also save to docs folder for GitHub backup
    docs_status = os.path.join("docs", "status.json")
    with open(docs_status, "w") as f:
        json.dump(data, f, indent=2)
    # Auto push to GitHub
    push_to_github()


def push_to_github():
    try:
        docs_dir = os.path.join(os.getcwd(), "docs")
        subprocess.run(["git", "add", "status.json"], check=True, capture_output=True, cwd=docs_dir)
        subprocess.run(["git", "commit", "-m", "Update status.json"], check=True, capture_output=True, cwd=docs_dir)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, cwd=docs_dir)
        print("[git] Auto-pushed status.json to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"[git] ERROR: {e}")
    except Exception as e:
        print(f"[git] ERROR: {e}")


def reset_daily():
    data = load_status()
    for task in data.get("tasks", []):
        task["status"] = "upcoming"
    data["lastUpdated"] = datetime.now().isoformat()
    save_status(data)
    print(f"[Reset] Daily reset at {datetime.now()}")


scheduler = BackgroundScheduler()
scheduler.add_job(reset_daily, "cron", hour=0, minute=0)
scheduler.start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/update", methods=["POST"])
def update():
    data = request.get_json()
    current = load_status()
    current.update(data)
    save_status(current)
    return jsonify({"ok": True})


def start_ngrok():
    try:
        ngrok.kill()
        time.sleep(2)
        tunnel = ngrok.connect(NGROK_PORT, domain=NGROK_DOMAIN)
        public_url = tunnel.public_url
        print(f"[ngrok] Tunnel active: {public_url}")
        data = load_status()
        data["ngrokUrl"] = public_url
        save_status(data)
        return tunnel
    except Exception as e:
        print(f"[ngrok] ERROR: {e}")
        print("[ngrok] Make sure you have added your authtoken:")
        print("        ngrok config add-authtoken <YOUR_TOKEN>")
        return None


if __name__ == "__main__":
    tunnel = start_ngrok()
    atexit.register(ngrok.kill)
    app.run(host="0.0.0.0", port=NGROK_PORT, debug=False)
