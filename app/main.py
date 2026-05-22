import json, re, pathlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
import httpx
from app.config import settings

app = FastAPI()
client = AsyncOpenAI(api_key=settings.openai_api_key)
BASE = pathlib.Path(__file__).parent

class AnalyzeRequest(BaseModel):
    url: str

def extract_video_id(url: str) -> str:
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("유효한 유튜브 URL이 아닙니다")

@app.get("/")
async def root():
    return FileResponse(BASE / "static/index.html")

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        video_id = extract_video_id(req.url)
    except ValueError as e:
        raise HTTPException(400, str(e))

    async with httpx.AsyncClient(timeout=15) as http:
        r = await http.get(
            "https://www.googleapis.com/youtube/v3/commentThreads",
            params={
                "part": "snippet",
                "videoId": video_id,
                "key": settings.youtube_api_key,
                "maxResults": 100,
                "order": "relevance",
                "textFormat": "plainText",
            }
        )

    data = r.json()

    if "error" in data:
        raise HTTPException(400, data["error"].get("message", "YouTube API 오류"))

    items = data.get("items", [])
    if not items:
        raise HTTPException(404, "댓글이 없거나 댓글이 비활성화된 영상입니다")

    comments = [
        item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        for item in items
    ]

    comments_text = "\n".join(f"- {c}" for c in comments[:60])

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "system",
                "content": "유튜브 댓글 분석 전문가입니다. JSON으로만 응답합니다."
            },
            {
                "role": "user",
                "content": f"""다음 유튜브 댓글들을 분석해주세요:

{comments_text}

다음 JSON 형식으로만 응답:
{{
    "positive_pct": 65,
    "negative_pct": 15,
    "neutral_pct": 20,
    "overall_sentiment": "긍정적/부정적/중립적/혼재",
    "sentiment_label": "반응이 뜨겁습니다 👍",
    "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
    "summary": "전반적인 댓글 반응 요약 (3문장)",
    "best_comment": "가장 공감을 많이 받을 만한 댓글 원문",
    "total_analyzed": 60
}}"""
            }
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(resp.choices[0].message.content)
    result["sample_comments"] = comments[:5]
    return JSONResponse(result)
