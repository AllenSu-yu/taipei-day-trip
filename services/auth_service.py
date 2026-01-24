# services/auth_service.py
import os
import datetime
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY 環境變數未設定")

class AuthService:
    """處理認證相關的業務邏輯"""
    
    @staticmethod
    def create_token(user):
        """產生 JWT token"""
        try:
            if isinstance(user, tuple):
                if len(user) < 3:
                    raise ValueError("元組長度不足，需要至少 3 個元素")
                user_id, user_name, user_email = user[0], user[1], user[2]
            else:
                user_id = user.id
                user_name = user.name
                user_email = user.email
        except (IndexError, AttributeError) as e:
            raise ValueError(f"無法從 user 物件取得必要資訊: {e}")
        
        payload = {
            "id": user_id,
            "name": user_name,
            "email": user_email,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    
    @staticmethod
    def verify_token(auth_header):
        """驗證 JWT token"""
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or not parts[1]:
            return None
        token = parts[1]
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded
        except InvalidTokenError:
            return None
