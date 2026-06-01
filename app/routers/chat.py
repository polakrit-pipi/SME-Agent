from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.langchain import CallbackHandler
import time # เพิ่มโมดูลจับเวลา

from app.dependencies import verify_shop, verify_jwt_auth
from app.config import settings
from app.services.ai_pipeline import get_or_create_prompt_cache, log_usage_to_supabase

router = APIRouter(prefix="/api/v1", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default-session"

@router.post("/chat")
async def chat_endpoint(
    payload: ChatRequest,
    background_tasks: BackgroundTasks,
    shop_id: str = Depends(verify_shop),
    auth_data: dict = Depends(verify_jwt_auth)
):
    # 1. ปรับข้อมูลจำลองให้ยาวเกิน 1,024 Tokens สำหรับการเทสต์
    base_kb = f"ข้อมูลร้าน {shop_id}: เสื้อยืดสีดำ 250 บาท, กางเกงยีนส์ 500 บาท, นโยบายคืนของภายใน 7 วัน. "
    shop_kb = base_kb * 100 # ✨ คูณ 100 รอบ เพื่อปั๊มความยาวให้เกินขีดจำกัดของ Gemini
    
    # 2. นำข้อความยาวๆ ไปสร้าง Cache
    cache_id = get_or_create_prompt_cache(shop_id, shop_kb)
    
    langfuse_handler = CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
        session_id=payload.session_id,
        tags=[f"shop_id:{shop_id}"]
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=settings.GEMINI_API_KEY
    )

    # ⏱️ เริ่มจับเวลา
    start_time = time.time()

    response = llm.invoke(
        [HumanMessage(content=payload.message)],
        config={"callbacks": [langfuse_handler]}
    )
    
    # ⏱️ สิ้นสุดจับเวลา และแปลงเป็นหน่วยมิลลิวินาที (ms)
    end_time = time.time()
    latency_ms = int((end_time - start_time) * 1000)

    langfuse_handler.flush()
    
    if response.usage_metadata:
        background_tasks.add_task(
            log_usage_to_supabase,
            shop_id=shop_id,
            session_id=payload.session_id,
            model="gemini-2.5-flash",
            usage_metadata=response.usage_metadata,
            latency_ms=latency_ms # ส่งตัวเลขเวลาไปที่ Database
        )

    return {
        "shop_id": shop_id,
        "reply": response.content,
        "status": "success"
    }