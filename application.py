from flask import Flask, render_template
import requests
import os
from collections import Counter

application = Flask(__name__)

API_URL = os.environ.get("TWEET_API_URL")

@application.route("/")
def index():
    try:
        response = requests.get(API_URL)
        tweets = response.json()

        user_counts = Counter(tweet["username"] for tweet in tweets)

        chart_labels = list(user_counts.keys())
        chart_values = list(user_counts.values())

        return render_template(
            "index.html",
            tweets=tweets,
            chart_labels=chart_labels,
            chart_values=chart_values
        )
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=8000)
