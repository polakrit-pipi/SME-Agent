import google.generativeai as genai
from google.generativeai import caching
from langchain_google_genai import ChatGoogleGenerativeAI
from app.database import supabase
from app.config import settings
import datetime
from google.api_core.exceptions import ResourceExhausted # ✨ นำเข้าตัวดักจับ Error

genai.configure(api_key=settings.GEMINI_API_KEY)

def get_or_create_prompt_cache(shop_id: str, knowledge_base_text: str):
    cache_name = f"shop_{shop_id}_kb"
    
    try:
        # 1. ลองค้นหา Cache เก่า
        for c in caching.CachedContent.list():
            if c.display_name == cache_name:
                return c.name
                
        # 2. ลองสร้างใหม่
        print(f"♻️ กำลังสร้าง Prompt Cache ใหม่ให้ร้าน {shop_id}...")
        new_cache = caching.CachedContent.create(
            model='models/gemini-2.5-flash',
            display_name=cache_name,
            system_instruction="คุณคือ AI Assistant ประจำร้านค้า ตอบคำถามโดยอิงจากข้อมูลต่อไปนี้",
            contents=[knowledge_base_text],
            ttl=datetime.timedelta(minutes=60),
        )
        return new_cache.name
        
    except ResourceExhausted:
        # ✨ ถ้าติด Limit บัญชีฟรี ให้ข้ามไปใช้งานแบบปกติ (ไม่พัง)
        print("⚠️ ข้ามการทำ Cache: บัญชี Free Tier ไม่รองรับฟีเจอร์นี้สำหรับโมเดลปัจจุบัน")
        return None
    except Exception as e:
        # ดัก Error อื่นๆ เผื่อไว้
        print(f"⚠️ ข้ามการทำ Cache: พบปัญหา {e}")
        return None

def log_usage_to_supabase(shop_id: str, session_id: str, model: str, usage_metadata: dict, latency_ms: int):
    """
    อัปเดตเวอร์ชันให้ส่ง latency_ms และ cached_tokens เข้า DB ด้วย
    """
    input_tok = usage_metadata.get("input_tokens", 0)
    output_tok = usage_metadata.get("output_tokens", 0)
    # ดึงค่า Token ที่ถูก Cache ไว้ (ถ้ามี)
    cached_tok = usage_metadata.get("cached_content_token_count", 0)
    
    cost_usd = ((input_tok / 1_000_000) * 0.30) + ((output_tok / 1_000_000) * 2.50)
    
    data = {
        "shop_id": shop_id,
        "session_id": session_id,
        "model": model,
        "input_tokens": input_tok,
        "output_tokens": output_tok,
        "cached_tokens": cached_tok, # คอลัมน์จากภาพ
        "cost_usd": round(cost_usd, 6),
        "cache_hit": False,
        "latency_ms": latency_ms     # คอลัมน์จากภาพ
    }
    
    supabase.table("token_usage").insert(data).execute()
    
    quota_res = supabase.table("shop_quota").select("used_tokens").eq("shop_id", shop_id).execute()
    if quota_res.data:
        current_used = quota_res.data[0]["used_tokens"]
        new_total = current_used + input_tok + output_tok
        supabase.table("shop_quota").update({"used_tokens": new_total}).eq("shop_id", shop_id).execute()