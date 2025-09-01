# api/webhook.py
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("")
def hello():
    return "Hello world :)"


@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook received:", data)

    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(debug=True)
