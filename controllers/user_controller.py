# controllers/user_controller.py
from models.user_model import UserModel
from services.auth_service import AuthService
from views.user_view import UserView

class UserController:
    """處理使用者相關的請求"""
    
    @staticmethod
    def signup(name, email, password):
        """註冊新使用者"""
        success, message = UserModel.create_user(name, email, password)
        
        if success:
            return UserView.format_signup_success()
        else:
            return UserView.format_signup_error(message)
    
    @staticmethod
    def login(email, password):
        """使用者登入"""
        try:
            user = UserModel.get_user_by_credentials(email, password)
            
            if user:
                token = AuthService.create_token(user)
                return UserView.format_login_success(token)
            else:
                return UserView.format_login_error("帳號不存在或密碼錯誤")
        except Exception as e:
            return UserView.format_login_error(f"登入失敗: {str(e)}")
    
    @staticmethod
    def check_auth(authorization):
        """檢查登入狀態"""
        if not authorization:
            return UserView.format_auth_check(None)
        
        user_info = AuthService.verify_token(authorization)
        return UserView.format_auth_check(user_info)
