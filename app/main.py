from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()

API_URL = "https://g9q41cdjsl.execute-api.us-east-1.amazonaws.com/dev/tweets"

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL)
        tweets = response.json() if response.status_code == 200 else []

    # Prepare data for chart
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
