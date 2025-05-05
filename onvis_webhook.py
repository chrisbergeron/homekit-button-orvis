import argparse
import yaml
from flask import Flask, request, jsonify
import subprocess
import requests

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.yml', help='Path to config file')
args = parser.parse_args()

# Load YAML config
with open(args.config, "r") as f:
    CONFIG = yaml.safe_load(f)

app = Flask(__name__)

@app.route("/api/onvis/<button_id>", methods=["POST"])
def handle_button(button_id):
    config = CONFIG.get(button_id)
    if not config:
        return jsonify({"error": "Unknown button"}), 404

    if config["type"] == "api":
        try:
            response = requests.request(
                method=config.get("method", "POST"),
                url=config["url"],
                headers=config.get("headers", {}),
                data=config.get("body", "")
            )
            print(f"[Webhook] Button {button_id} called API: {response.status_code}")
        except Exception as e:
            print(f"[Error] API call for {button_id} failed: {e}")
            return jsonify({"error": "API call failed"}), 500

    elif config["type"] == "shell":
        try:
            subprocess.Popen(config["command"], shell=True)
            print(f"[Webhook] Button {button_id} ran shell command.")
        except Exception as e:
            print(f"[Error] Shell command failed: {e}")
            return jsonify({"error": "Shell command failed"}), 500

    else:
        return jsonify({"error": "Invalid config type"}), 400

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055)
