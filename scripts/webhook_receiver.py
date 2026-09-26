"""Optional local Flask receiver for webhook demonstrations."""

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.post("/notify")
def notify():
    payload = request.get_json(silent=True) or {}
    print("Webhook received:")
    print(payload)
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)