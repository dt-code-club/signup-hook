from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string
from datetime import datetime
import os
import json

app = Flask(__name__)
cert_json = os.environ.get("FIREBASE_CERT_JSON")
if not cert_json:
    raise RuntimeError("FIREBASE_CERT_JSON environment variable not set.")
cert_dict = json.loads(cert_json)
cred = credentials.Certificate(cert_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()


@app.route("/")
def index():
    return "balls"


def randomstring(n, alpha=True, numeric=True, symbolic=True):
    chars = ""
    if alpha:
        chars += string.ascii_letters
    if numeric:
        chars += string.digits
    if symbolic:
        chars += string.punctuation
    if not chars:
        raise ValueError("At least one character set must be enabled.")
    return ''.join(random.choices(chars, k=n))


@app.route("/api/webhook")
def webhook():
    data = request.json
    main_form = data["form_response"]
    formfields = main_form["definition"]["fields"]
    fields = {}
    answers = {}
    for field in formfields:
        title = field.get("title")
        id = field.get("id")
        fields[id] = title
    for answer in main_form["answers"]:
        answerid = answer["field"]["id"]
        answer = answer[answer["type"]]
        fieldname = fields[answerid]
        answers[answerid] = {
            "name": fieldname,
            "value": answer
        }
    print(answers)
    userinfo = {
        "firstname": "Test Name",
        "lastname": "Test Name",
        "signup": datetime.utcnow()
    }
    userid = randomstring(20)
    db.collection("members").add(userinfo, userid)
    return {"status": "received"}


if __name__ == "__main__":
    app.run(debug=True)
