from typing import Annotated
from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from app.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import supabase # Import supabase ที่เพิ่งสร้างมาใช้

security = HTTPBearer()

async def verify_shop(x_shop_id: Annotated[str | None, Header(alias="X-Shop-ID")] = None):
    if not x_shop_id:
        raise HTTPException(status_code=400, detail="X-Shop-ID header missing")
    
    # ดึงข้อมูลโควตาของร้านจาก Supabase (อ้างอิงตาราง shop_quota ตาม Work Plan)
    try:
        response = supabase.table("shop_quota").select("monthly_tokens, used_tokens").eq("shop_id", x_shop_id).execute()
        
        # ถ้าร้านนี้มีข้อมูลอยู่ในระบบ
        if response.data:
            quota = response.data[0]
            # เช็คว่าใช้เกินที่กำหนดรายเดือนหรือยัง
            if quota["used_tokens"] >= quota["monthly_tokens"]:
                raise HTTPException(status_code=403, detail="โควตา Token ประจำเดือนเต็มแล้ว กรุณาอัปเกรดแพ็กเกจ")
        else:
            # กรณีหาร้านไม่เจอใน DB
            raise HTTPException(status_code=404, detail="ไม่พบรหัสร้านค้านี้ในระบบ")
            
    except Exception as e:
        # ดักจับ Error กรณีต่อ DB ไม่ติด
        print(f"Database Error: {e}")
        
    return x_shop_id

async def verify_jwt_auth(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    """
    ตรวจสอบและถอดรหัส JWT Token ที่ส่งมาจากฝั่ง Frontend หรือ Client
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return payload
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Could not validate credentials")