"""Optional local Flask receiver for webhook demonstrations.

This is a tiny stand-in for a real webhook consumer. Run it locally when you
want to see prediction payloads without starting the full Docker Compose stack.
It is not used by docker-compose.yml; Compose uses httpbin instead.
"""

from flask import Flask, jsonify, request

# Create a Flask application instance. __name__ tells Flask where to look for
# templates and static files; here it is just a minimal API.
app = Flask(__name__)


@app.post("/notify")
def notify():
    """Receive a JSON webhook and echo it to the console."""
    # silent=True prevents Flask from raising an error if the body is not JSON.
    payload = request.get_json(silent=True) or {}
    print("Webhook received:")
    print(payload)
    # Return a small JSON acknowledgement with HTTP 200.
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    # Listen on all interfaces so containers or other machines can reach it.
    # debug=False avoids the interactive debugger in production-like demos.
    app.run(host="0.0.0.0", port=5000, debug=False)