from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests
import re

app = FastAPI()

# ---------------- CONFIG ----------------
API_KEY = "uncommoncore"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------- API KEY CHECK ----------------
def verify_key(request: Request):
    key = request.headers.get("x-api-key")
    
    if key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key"
        )

# ---------------- HOME ----------------
@app.get("/")
def home():
    return {
        "creator": "@uncommonexe",
        "release_channel": "@uncommoncore",
        "status": "running",
        "endpoints": {
            "pinterest_download": "/pinterest?url=<pin_url>",
            "headers_required": {
                "x-api-key": "uncommoncore"
            }
        }
    }

# ---------------- PINTEREST DOWNLOADER ----------------
@app.get("/pinterest")
def pinterest_downloader(url: str, request: Request):
    verify_key(request)

    try:
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to fetch Pinterest URL"}
            )

        html = response.text

        video_match = re.search(
            r'"contentUrl":"(https:[^\\"]+\\.mp4[^"]*)"',
            html
        )

        image_match = re.search(
            r'"image":"(https:[^\\"]+)"',
            html
        )

        video_url = None
        image_url = None

        if video_match:
            video_url = video_match.group(1).replace('\\u002F', '/')

        if image_match:
            image_url = image_match.group(1).replace('\\u002F', '/')

        if not video_url and not image_url:
            return JSONResponse(
                status_code=404,
                content={"error": "No media found"}
            )

        return {
            "status": True,
            "video": video_url,
            "image": image_url
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
