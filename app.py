import os
import json
import requests
from flask import Flask, render_template

app = Flask(__name__)

API_URL = os.getenv("TWEET_API_URL", "http://localhost:3000/tweets")

@app.route("/")
def index():
    try:
        response = requests.get(API_URL)
        tweets = response.json() if response.status_code == 200 else []
    except Exception as e:
        tweets = []
        print(f"Error fetching tweets: {e}")

    # Hitung jumlah tweet per user
    counts = {}
    for tweet in tweets:
        user = tweet.get("username", "unknown")
        counts[user] = counts.get(user, 0) + 1

    chart_data = {
        "labels": list(counts.keys()),
        "values": list(counts.values())
    }

    return render_template("index.html", tweets=tweets, chart_data=chart_data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
