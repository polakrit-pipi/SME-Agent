from jose import jwt
import time

# ⚠️ เปลี่ยนค่านี้ให้ตรงกับ JWT_SECRET ที่คุณก๊อปมาจาก Supabase
SECRET_KEY = "slyYBzsxOwM0EwzISjyyNffML0U+E5f5KTp8ml6QhCiYyaao0nlmvnK4GwALY2cL5IzpLGHPKHXUxHxwSObUvg=="

payload = {
    "sub": "user_123",           # รหัสสมมติของเจ้าของร้าน
    "exp": int(time.time()) + 3600    # ให้กุญแจมีอายุ 1 ชั่วโมง
}

# ปั๊มกุญแจ
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print("เอา Token นี้ไปใช้เทสต์ได้เลยครับ:\n")
print(f"Bearer {token}")