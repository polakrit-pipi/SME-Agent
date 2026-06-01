from typing import Annotated
from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from app.config import settings

async def verify_shop(x_shop_id: Annotated[str | None, Header(alias="X-Shop-ID")] = None):
    """
    ตรวจสอบว่ามีการส่ง Header X-Shop-ID มาหรือไม่ 
    (ในเฟสถัดไป AI Eng #1 สามารถใส่ Logic ตรวจสอบความถูกต้องกับตารางใน Supabase ได้ที่นี่)
    """
    if not x_shop_id:
        raise HTTPException(status_code=400, detail="X-Shop-ID header missing")
    return x_shop_id

async def verify_jwt_auth(authorization: Annotated[str | None, Header()] = None):
    """
    ตรวจสอบและถอดรหัส JWT Token ที่ส่งมาจากฝั่ง Frontend หรือ Client
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token_type, token = authorization.split(" ")
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return payload
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Could not validate credentials")