from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string
from datetime import datetime, timezone
import os
import json

app = Flask(__name__)
cert_json = os.environ.get("fbcert")
if not cert_json:
    raise RuntimeError("FIREBASE_CERT_JSON environment variable not set.")
cert_dict = json.loads(cert_json)
cred = credentials.Certificate(cert_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

multiseltypes = ["MULTIPLE_CHOICE", "MULTI_SELECT", "DROPDOWN"]


@app.route("/")
def index():
    return "balls"


def randomstring(n: int, alpha=True, numeric=True, symbolic=True):
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


def processmulti(choices: list, options: list):
    answers = []
    for choice in choices:
        result = list(filter(lambda x: x["id"] == choice, options))[0]["text"]
        if (result in ["Yes", "No"]):
            result = True if result == "Yes" else False
        answers.append(result)
    print(answers)
    if (len(answers) == 1):
        return answers[0]
    else:
        return answers


@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.json
    formfields = data["data"]["fields"]
    answers = {}
    for field in formfields:
        key = field["key"].replace("question_", "")
        question = field["label"]
        if (field.get("type", "INPUT_TEXT") in multiseltypes):
            answer = processmulti(field["value"], field["options"])
        else:
            answer = field["value"]
        answers[key] = {
            "label": question,
            "answer": answer
        }
    userinfo = {
        "firstname": answers.get("jl5Md4", ""),
        "lastname": answers.get("2K1kq9", ""),
        "email": answers.get("xJ4Qk5", ""),
        "signuptime": datetime.now(tz=timezone.utc),
        "grade": answers.get("Z2vV4B", ""),
        "previous_experience": answers.get("N7MVKj", ""),
        "langs": answers.get("qRoBx9", ""),
        "goals": answers.get("VzvVGM", ""),
        "questions": answers.get("PzvlpB", "")
    }
    userid = randomstring(20, symbolic=False)
    userdoc = db.collection("members").document(userid)
    userdoc.set(userinfo)
    return {"status": "received"}


if __name__ == "__main__":
    app.run(debug=True)
