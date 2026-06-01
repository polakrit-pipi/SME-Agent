from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.dependencies import verify_shop, verify_jwt_auth
from app.config import settings

# Import เครื่องมือฝั่ง AI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler

router = APIRouter(prefix="/api/v1", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = "default-session"

@router.post("/chat")
async def chat_endpoint(
    payload: ChatRequest,
    shop_id: str = Depends(verify_shop),
    auth_data: dict = Depends(verify_jwt_auth)
):
    """
    Endpoint สำหรับรับข้อความและส่งต่อให้ Gemini ประมวลผล พร้อมเก็บ Log ลง Langfuse
    """
    
    # 1. ตั้งค่า Langfuse (สร้าง Handler ใหม่ทุกครั้งที่โดนเรียก เพื่อแยก Trace ให้ชัดเจน)
    langfuse_handler = CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
        session_id=payload.session_id, # เก็บ Session ID เพื่อรู้ว่าเป็นลูกค้ารายเดียวกัน
        tags=[f"shop_id:{shop_id}"]    # ✨ จุดเด่น: แปะป้ายบอก Langfuse ว่าบิลนี้ของร้านไหน!
    )

    # 2. เรียกใช้ LLM (Gemini 2.5 Flash)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=settings.GEMINI_API_KEY
    )

    # 3. ส่งข้อความไปหา AI และฝังตัวดักจับ (Callback) ของ Langfuse
    response = llm.invoke(
        [HumanMessage(content=payload.message)],
        config={"callbacks": [langfuse_handler]}
    )

    # 4. บังคับให้ Langfuse อัปโหลด Log ขึ้นเซิร์ฟเวอร์ทันที
    langfuse_handler.flush()

    # 5. ส่งคำตอบกลับไปหาฝั่งผู้ใช้งาน (Frontend / LINE)
    return {
        "shop_id": shop_id,
        "reply": response.content,
        "status": "success"
    }