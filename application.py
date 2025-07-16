from flask import Flask, render_template, request, redirect, url_for, make_response
import requests
import os
import boto3
import jwt
from collections import Counter

application = Flask(__name__)

API_URL = os.environ.get("TWEET_API_URL")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
USER_POOL_ID = os.environ.get("USER_POOL_ID")

cognito = boto3.client("cognito-idp", region_name="us-east-1")

def is_token_valid(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return "email" in payload
    except Exception:
        return False

@application.route("/")
def home():
    token = request.cookies.get("id_token")
    if token and is_token_valid(token):
        return redirect("/index")
    return redirect("/login")

@application.route("/index")
def index():
    token = request.cookies.get("id_token")
    if not token or not is_token_valid(token):
        return redirect("/login")

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(API_URL, headers=headers)
        tweets = response.json()

        # Tambahkan validasi bahwa response harus list
        if not isinstance(tweets, list):
            raise ValueError(f"Unexpected response format: {tweets}")

        user_counts = Counter(tweet["username"] for tweet in tweets)
        chart_labels = list(user_counts.keys())
        chart_values = list(user_counts.values())

        return render_template("index.html", tweets=tweets, chart_labels=chart_labels, chart_values=chart_values)
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
            res = make_response(redirect("/index"))
            res.set_cookie("id_token", id_token, httponly=True)
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
    return res

@application.route("/post_tweet", methods=["POST"])
def post_tweet():
    token = request.cookies.get("id_token")
    if not token or not is_token_valid(token):
        return redirect("/login")

    username = request.form.get("username")
    tweet = request.form.get("tweet")
    if username and tweet:
        payload = {"username": username, "tweet": tweet}
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                return redirect(url_for('index'))
            else:
                return f"Error posting tweet: {response.text}", 500
        except Exception as e:
            return f"Request error: {e}", 500
    else:
        return "Username and tweet cannot be empty", 400

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=8000)
