"""
Honey LaRva AI Chatbot API Backend
FastAPI + Claude API
起動: uvicorn chatbot_api:app --host 0.0.0.0 --port 8080
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://honeylarva.com", "https://www.honeylarva.com", "*"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """あなたはHoney LaRva（ハニーラーバ）フィットネスボクシングジムの公式AIアシスタントです。
以下の情報をもとに、丁寧・明るく・簡潔に回答してください（200文字以内を目安）。
絵文字を適度に使い、親しみやすい口調で。

【ジム基本情報】
- ジム名：Honey LaRva（ハニーラーバ）フィットネスボクシング
- 場所：栃木県大田原市・那須塩原市（2拠点）
- 公式HP：https://honeylarva.com/
- コンセプト：ボクシングの動きで骨盤・呼吸を整えるフィットネスジム

【クラス種類】
- 一般クラス：骨盤・呼吸意識のフィットネスプログラム
- ジュニアクラス：多様性重視の基礎トレーニング（小中学生）
- シニアクラス（ミドルクラス）：60歳以上対象
- 出張講座：健康講演・骨盤底筋トレーニング指導

【体験レッスン】
- 料金：¥2,000（1回）
- 大田原店・黒磯店とも営業時間内であればいつでも参加OK
- 予約先：https://honeylarva.com/contact

【料金プラン（税込）】
- 一般コース：月4回 ¥6,000 / 月8回 ¥7,000 / フリー会員 ¥10,000（大田原・黒磯 共通）
- ジュニア（小中学生）：月4回 ¥5,000 / 月8回 ¥7,000
- シニア（60歳以上）：¥8,000
- パーソナルトレーニング：60分 ¥10,000
- オンラインダイエット：月額 ¥13,000
⚠️大田原・黒磯とも一般会員は新規入会を一時停止中。ジュニアは受付中。
空きができ次第、予約された方を優先してご案内。予約先：https://honeylarva.com/contact

【フランチャイズ】
Honey LaRvaのフランチャイジーとして加入し、自分の地域でジムを開業できます。
研修サポート・集客支援・継続コンサルティングあり。

詳細な料金や具体的な日程は「公式HPまたは直接お問い合わせください」と案内してください。"""


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        history = [{"role": m.role, "content": m.content} for m in req.messages[-10:]]
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        reply = response.content[0].text
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
