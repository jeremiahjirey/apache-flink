import os
import requests
from flask import Flask, render_template

app = Flask(__name__)

# Ambil URL dari environment variable
API_URL = os.getenv("TWEET_API_URL", "http://localhost:3000/tweets")

@app.route("/")
def index():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        tweets = response.json()
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        tweets = []

    # Hitung jumlah tweet per user
    counts = {}
    for tweet in tweets:
        user = tweet.get("username", "unknown")
        counts[user] = counts.get(user, 0) + 1

    chart_data = {
        "labels": list(counts.keys()),
        "values": list(counts.values())  # ✅ Panggil .values()
    }

    return render_template("index.html", tweets=tweets, chart_data=chart_data)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
