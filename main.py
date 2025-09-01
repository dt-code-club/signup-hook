from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return "balls"


@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook received:", data)

    # ✅ Acknowledge quickly so Typeform doesn’t retry
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(debug=True)
