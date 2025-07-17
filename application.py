from flask import Flask, render_template, request, redirect, url_for, make_response
import requests
import os
import boto3
import jwt
from collections import Counter
from datetime import datetime, timedelta

application = Flask(__name__)

API_URL = os.environ.get("TWEET_API_URL")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
USER_POOL_ID = os.environ.get("USER_POOL_ID")
AUTH_SECRET = os.environ.get("AUTH_SECRET")
ID_TOKEN_EXPIRED = int(os.environ.get("COGNITO_ID_TOKEN_EXPIRED", 3600))  # default 1 hour

cognito = boto3.client("cognito-idp", region_name="us-east-1")

# Helper untuk verifikasi id_token tanpa signature check (frontend login)
def is_token_valid(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return "email" in payload
    except Exception:
        return False

# Helper untuk membuat session_token custom
def create_session_token(email):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(seconds=ID_TOKEN_EXPIRED)
    }
    return jwt.encode(payload, AUTH_SECRET, algorithm="HS256")

# Helper untuk validasi session_token
def verify_session_token(token):
    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
        return payload.get("email")
    except jwt.ExpiredSignatureError:
        return None
    except Exception:
        return None

@application.route("/")
def home():
    session_token = request.cookies.get("session_token")
    email = verify_session_token(session_token)
    if email:
        return redirect("/index")
    return redirect("/login")

@application.route("/index")
def index():
    session_token = request.cookies.get("session_token")
    email = verify_session_token(session_token)
    if not email:
        return redirect("/login")

    id_token = request.cookies.get("id_token")
    headers = {"Authorization": f"Bearer {id_token}"}

    try:
        response = requests.get(API_URL, headers=headers)
        tweets = response.json()

        if isinstance(tweets, dict) and tweets.get("message") == "Unauthorized":
            return f"Invalid tweet data: {tweets}", 401

        user_counts = Counter(tweet["username"] for tweet in tweets if isinstance(tweet, dict))
        chart_labels = list(user_counts.keys())
        chart_values = list(user_counts.values())

        return render_template(
            "index.html",
            tweets=tweets,
            chart_labels=chart_labels,
            chart_values=chart_values,
            email=email
        )
    except Exception as e:
        return f"Error loading index: {e}", 500

@application.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            resp = cognito.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": email, "PASSWORD": password}
            )
            id_token = resp["AuthenticationResult"]["IdToken"]
            session_token = create_session_token(email)

            res = make_response(redirect("/index"))
            res.set_cookie("id_token", id_token, httponly=True)
            res.set_cookie("session_token", session_token, httponly=True)
            return res
        except Exception as e:
            return f"Login error: {e}", 401

    return render_template("login.html")

@application.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            cognito.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=email,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "name", "Value": name}
                ]
            )
            return redirect("/confirm")
        except Exception as e:
            return f"Signup error: {e}", 400
    return render_template("signup.html")

@application.route("/confirm", methods=["GET", "POST"])
def confirm():
    if request.method == "POST":
        email = request.form.get("email")
        code = request.form.get("code")
        try:
            cognito.confirm_sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=email,
                ConfirmationCode=code
            )
            return redirect("/login")
        except Exception as e:
            return f"Confirmation error: {e}", 400
    return render_template("confirm.html")

@application.route("/logout")
def logout():
    res = make_response(redirect("/login"))
    res.set_cookie("id_token", "", expires=0)
    res.set_cookie("session_token", "", expires=0)
    return res

@application.route("/post_tweet", methods=["POST"])
def post_tweet():
    session_token = request.cookies.get("session_token")
    email = verify_session_token(session_token)
    if not email:
        return redirect("/login")

    id_token = request.cookies.get("id_token")
    headers = {"Authorization": f"Bearer {id_token}"}

    username = request.form.get("username")
    tweet = request.form.get("tweet")
    if username and tweet:
        payload = {"username": username, "tweet": tweet}
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                return redirect(url_for("index"))
            else:
                return f"Invalid tweet data: {response.json()}", 401
        except Exception as e:
            return f"Request error: {e}", 500
    else:
        return "Username and tweet cannot be empty", 400

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=8000)
