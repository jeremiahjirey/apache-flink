import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_URL = os.getenv("TWEET_API_URL", "http://localhost:3000/tweets")  # default saat dev lokal

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL)
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

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tweets": tweets,
        "chart_data": chart_data
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
