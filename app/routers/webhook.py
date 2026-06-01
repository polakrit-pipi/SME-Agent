from fastapi import APIRouter, Request, status, BackgroundTasks

router = APIRouter(prefix="/webhook", tags=["Webhook"])

@router.post("/line")
async def line_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint หลักสำหรับรับ Event จาก LINE Messaging API
    """
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")
    
    # TODO: [AI Eng #2] จะมาเขียนระบบแกะข้อความและเรียกใช้งาน Agent ตรงส่วนนี้
    
    return {"status": "success"}