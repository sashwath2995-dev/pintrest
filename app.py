from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests
import re
import traceback
import yt_dlp

app = FastAPI()

# ================= CONFIG =================
API_KEY = "uncommoncore"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ================= API KEY =================
def verify_key(request: Request):
    key = request.headers.get("x-api-key")

    if key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key"
        )

# ================= HOME =================
@app.get("/")
def home():
    return {
        "creator": "@uncommonexe",
        "release_channel": "@uncommoncore",
        "status": "running",
        "endpoints": {
            "pinterest": "/pinterest?url=PIN_URL",
            "youtube": "/youtube?url=VIDEO_URL",
            "instagram": "/instagram?url=POST_URL"
        },
        "headers": {
            "x-api-key": "uncommoncore"
        }
    }

# ================= PINTEREST =================
@app.get("/pinterest")
def pinterest_downloader(url: str, request: Request):
    verify_key(request)

    try:
        response = requests.get(url, headers=HEADERS)
        html = response.text

        video_match = re.search(
            r'"contentUrl":"(https:[^"]+\.mp4[^"]*)"',
            html
        )

        image_match = re.search(
            r'"image":"(https:[^"]+)"',
            html
        )

        video_url = (
            video_match.group(1).replace("\\u002F", "/")
            if video_match else None
        )

        image_url = (
            image_match.group(1).replace("\\u002F", "/")
            if image_match else None
        )

        return {
            "status": True,
            "video": video_url,
            "image": image_url
        }

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }

# ================= YOUTUBE =================
@app.get("/youtube")
def youtube_downloader(url: str, request: Request):
    verify_key(request)

    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []

        for f in info.get("formats", []):
            file_url = f.get("url")

            if file_url:
                formats.append({
                    "quality": str(f.get("format_note")),
                    "url": file_url
                })

        return {
            "status": True,
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "formats": formats[:10]
        }

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }

# ================= INSTAGRAM =================
@app.get("/instagram")
def instagram_downloader(url: str, request: Request):
    verify_key(request)

    try:
        response = requests.get(url, headers=HEADERS)
        html = response.text

        video_match = re.search(
            r'"video_url":"([^"]+)"',
            html
        )

        image_match = re.search(
            r'"display_url":"([^"]+)"',
            html
        )

        video_url = (
            video_match.group(1)
            .replace("\\u0026", "&")
            .replace("\\/", "/")
            if video_match else None
        )

        image_url = (
            image_match.group(1)
            .replace("\\u0026", "&")
            .replace("\\/", "/")
            if image_match else None
        )

        return {
            "status": True,
            "video": video_url,
            "image": image_url
        }

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }
