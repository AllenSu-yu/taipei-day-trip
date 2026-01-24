# views/common_view.py
class CommonView:
    """處理通用的回應格式"""
    
    @staticmethod
    def format_error(message):
        """格式化錯誤回應"""
        return {
            "error": True,
            "message": message
        }
    
    @staticmethod
    def format_success():
        """格式化成功回應"""
        return {"ok": True}
    
    @staticmethod
    def format_not_authorized():
        """格式化未授權回應"""
        return {
            "error": True,
            "message": "未授權"
        }
    
    @staticmethod
    def format_not_logged_in():
        """格式化未登入回應"""
        return {
            "error": True,
            "message": "尚未登入"
        }
