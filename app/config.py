from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Phase 1: Database & Auth
    SUPABASE_URL: str = "https://placeholder.supabase.co"
    SUPABASE_KEY: str = "placeholder_key"
    JWT_SECRET: str = "placeholder_secret"
    ALGORITHM: str = "HS256"
    
    # Phase 2: AI & Observability (เพิ่มเข้ามาใหม่)
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore" # ใส่ไว้กัน Error เวลามีตัวแปรอื่นๆ แทรกใน .env

settings = Settings()