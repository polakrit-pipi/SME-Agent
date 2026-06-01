from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.dependencies import verify_shop, verify_jwt_auth

router = APIRouter(prefix="/api/v1", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@router.post("/chat")
async def chat_endpoint(
    payload: ChatRequest,
    shop_id: str = Depends(verify_shop),
    auth_data: dict = Depends(verify_jwt_auth)
):
    """
    Endpoint แชทของแอปพลิเคชันหลัก 
    ต้องการ X-Shop-ID ใน Header และการแนบ Bearer Token
    """
    # TODO: [AI Eng #2] นำข้อความส่งต่อไปเข้ากระบวนการ LangChain + Prompt Caching
    return {
        "shop_id": shop_id,
        "reply": f"ระบบได้รับข้อความ '{payload.message}' แล้ว กำลังประมวลผลผ่าน Agent...",
        "status": "processing"
    }