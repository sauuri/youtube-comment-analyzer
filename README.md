# 💬 YouTube Comment Analyzer

> YouTube Data API + GPT-4o-mini 기반 댓글 감성 분석기

YouTube URL을 입력하면 AI가 댓글을 수집하고 긍정/부정/중립 비율, 키워드, 요약, 베스트 댓글을 분석해줍니다.

## 📸 Demo

![demo](demo.gif)

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| LLM | OpenAI GPT-4o-mini |
| Comments API | YouTube Data API v3 |
| Backend | FastAPI |
| Frontend | Vanilla JS |
| Deploy | Render |

## 🚀 실행 방법

```bash
git clone https://github.com/sauuri/youtube-comment-analyzer
cd youtube-comment-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 OPENAI_API_KEY, YOUTUBE_API_KEY 입력
uvicorn app.main:app --reload
```

브라우저에서 `http://localhost:8000` 열기

## 🔗 Live Demo

[https://youtube-comment-analyzer-1-f34e.onrender.com](https://youtube-comment-analyzer-1-f34e.onrender.com)
