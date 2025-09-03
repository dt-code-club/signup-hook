import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from flask import Flask, request, render_template
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string
from datetime import datetime, timedelta, timezone
import os
import json
import threading

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
    return render_template("index.html")


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
    if (choices == None):
        return []
    for choice in choices:
        result = list(filter(lambda x: x["id"] == choice, options))[0]["text"]
        if (result in ["Yes", "No"]):
            result = True if result == "Yes" else False
        answers.append(result)
    if (len(answers) == 1):
        return answers[0]
    else:
        return answers


def sendwelcome(response: dict):
    userinfo = {}
    for item in response.keys():
        if (item == "signuptime"):
            continue
        userinfo[item] = response[item]["answer"]

    print(f"Preparing to send welcome email to: {userinfo.get('email')}")
    username = os.environ.get("app_email")
    password = os.environ.get("app_pw")
    print(f"Using app_email: {username}")

    try:
        print("Connecting to SMTP server...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', smtplib.SMTP_SSL_PORT)
        server.set_debuglevel(1)
        server.ehlo()
        print("Logging in to SMTP server...")
        server.login(username, password)
    except Exception as e:
        print(f"SMTP connection/login failed: {e}")
        return

    msg = EmailMessage()

    msg_id = make_msgid()
    msg['Message-ID'] = msg_id
    msg.add_header('Content-Type', 'text/html')
    msg['In-Reply-To'] = ''
    msg['References'] = ''
    msg['Subject'] = "Welcome to Code Club!"
    msg['From'] = "David Thompson Code Club"
    msg['To'] = f"{userinfo['firstname']} {userinfo['lastname']} <{userinfo['email']}>"
    body = f'''Hey {userinfo['firstname']},<br>
    {"Welcome to Code Club, and to your first year of school at David Thompson!" if userinfo["grade"]=="8" else "Welcome to Code Club."} I'm Aaron, the 2025-2026 president of Code Club, and I created this system that allows you to sign up for our club. 
    You've chosen {"to receive our newsletters and other information through email, so you'll receive more email just like this in the future." if userinfo["newsletter"] else "not to receive any email at this address, so you won't receive any more email like this in the future."}
    <br><br>
    In the past few years, our recruitment numbers have been down, as well as our meeting attendance. This year,
    the executive team is working to overhaul the club and make your experience the best it can be, and keep it
    that way in the future. We would love to hear what ideas you guys have for this club. We're glad to have you
    here, and we'd like to chat more. I would like to extend this exclusive invitation to our cozy little
    Discord server: <a href="https://discord.gg/q6cT42vcTm">discord.gg/q6cT42vcTm</a> <br><br>
    Thank you for your interest in our club! We hope to see you at the next meeting! :) <br><br>
    <img width="300"
        src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXNxdDBneDR5em9peWwxb3VucDA2aXk5MjhqcnM0cXZsMDRlYnd3OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/13HgwGsXF0aiGY/giphy.gif">
    <br><br>
    Aaron Wong<br>
    DTCC Club President, 2025-2026
    '''
    try:
        with open("./welcome.html", "r") as file:
            email_body = file.read()
        email_body = email_body.replace("[body]", body)
        msg.set_payload(email_body.encode('utf-8'))
        print("Sending email message...")
        server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


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
        "questions": answers.get("PzvlpB", ""),
        "newsletter": answers.get("ExvNXN", "")
    }
    userid = randomstring(20, symbolic=False)
    userdoc = db.collection("members").document(userid)
    userdoc.set(userinfo)
    threading.Thread(target=sendwelcome, args=(userinfo,)).start()
    return {"status": "received"}


if __name__ == "__main__":
    app.run(debug=True)
