import json, pathlib, itertools
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from app.config import settings

app = FastAPI()
client = AsyncOpenAI(api_key=settings.openai_api_key)
BASE = pathlib.Path(__file__).parent

class AnalyzeRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return FileResponse(BASE / "static/index.html")

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        downloader = YoutubeCommentDownloader()
        gen = downloader.get_comments_from_url(req.url, sort_by=SORT_BY_POPULAR)
        comments = [c["text"] for c in itertools.islice(gen, 80)]
    except Exception as e:
        raise HTTPException(400, f"댓글을 가져올 수 없습니다: {str(e)}")

    if not comments:
        raise HTTPException(404, "댓글이 없거나 비공개 영상입니다")

    comments_text = "\n".join(f"- {c}" for c in comments[:60])

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "system",
                "content": "유튜브 댓글 분석 전문가입니다. 댓글의 감성과 주요 반응을 분석하고 JSON으로만 응답합니다."
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
