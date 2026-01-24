# views/user_view.py
from views.common_view import CommonView

class UserView:
    """處理使用者相關的回應格式"""
    
    @staticmethod
    def format_signup_success():
        """格式化註冊成功回應"""
        return CommonView.format_success()
    
    @staticmethod
    def format_signup_error(message):
        """格式化註冊失敗回應"""
        return CommonView.format_error(message)
    
    @staticmethod
    def format_login_success(token):
        """格式化登入成功回應"""
        return {"token": token}
    
    @staticmethod
    def format_login_error(message):
        """格式化登入失敗回應"""
        return CommonView.format_error(message)
    
    @staticmethod
    def format_auth_check(user_info):
        """格式化認證檢查回應"""
        if user_info:
            return {
                "data": {
                    "id": user_info.get("id"),
                    "name": user_info.get("name"),
                    "email": user_info.get("email")
                }
            }
        return {"data": None}
