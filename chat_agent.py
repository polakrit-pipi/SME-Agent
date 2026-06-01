
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

print("⏳ กำลังเชื่อมต่อระบบ SME AI Agent...")

# 1. สร้างตัวดักจับ (Handler) ของ Langfuse
langfuse_handler = CallbackHandler(
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
    host=os.environ.get("LANGFUSE_HOST")
)

# 2. ตั้งค่า LangChain ให้เรียกใช้ Gemini 2.5 Flash
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3, # ใช้ 0.3 เพื่อให้คำตอบนิ่งและเป็นทางการ เหมาะกับงานตอบลูกค้า
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

print("✅ ระบบพร้อมใช้งาน! (พิมพ์ 'exit' เพื่อออก)\n" + "-"*40)

# 3. สร้าง Basic Chat Loop ทดสอบการสนทนา
while True:
    user_input = input("👤 Customer: ")
    if user_input.lower() in ['exit', 'quit']:
        print("👋 ปิดระบบสนทนา")
        break
        
    # โยนคำถามให้ LLM และแนบ langfuse_handler เข้าไปด้วย!
    response = llm.invoke(
        [HumanMessage(content=user_input)],
        config={"callbacks": [langfuse_handler]}
    )
    
    print(f"🤖 Agent: {response.content}\n")

# บังคับให้ส่ง Log ล็อตสุดท้ายขึ้นเซิร์ฟเวอร์ก่อนปิดโปรแกรม
langfuse_handler.flush()