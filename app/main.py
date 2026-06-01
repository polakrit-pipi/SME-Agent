from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import webhook, chat

app = FastAPI(
    title="SME AI Agent API Gateway",
    description="ระบบ Backend หลักรองรับ Token Monitoring, Caching และ Agent Pipelines",
    version="1.0.0"
)

# เปิด CORS เพื่อให้ตัวแดชบอร์ด Next.js สามารถยิงมาติดต่อได้โดยตรง
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ในขั้นตอน Production ควรระบุโดเมนให้เฉพาะเจาะจง
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
def health_check():
    """
    เช็คความพร้อมการทำงานของ Server (สำหรับให้ Railway ใช้ตรวจสุขภาพแอป)
    """
    return {"status": "ok", "message": "SME AI Agent Pipeline is operational"}

# รวมศูนย์ Routers จากโฟลเดอร์ต่างๆ
app.include_router(webhook.router)
app.include_router(chat.router)