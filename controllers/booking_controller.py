# controllers/booking_controller.py
from models.booking_model import BookingModel
from services.auth_service import AuthService
from views.booking_view import BookingView
from views.common_view import CommonView

class BookingController:
    """處理預定行程相關的請求"""
    
    @staticmethod
    def get_booking(authorization):
        """取得預定行程"""
        if not authorization:
            return CommonView.format_not_logged_in()
        
        user_info = AuthService.verify_token(authorization)
        if not user_info:
            return CommonView.format_not_authorized()
        
        try:
            member_id = user_info.get("id")
            booking_data = BookingModel.get_booking_by_member_id(member_id)
            
            if not booking_data:
                return BookingView.format_booking_not_found()
            
            return BookingView.format_booking_detail(booking_data)
            
        except Exception as e:
            return CommonView.format_error(str(e))
    
    @staticmethod
    def create_booking(booking_data, authorization):
        """建立預定行程"""
        if not authorization:
            return CommonView.format_not_logged_in()
        
        user_info = AuthService.verify_token(authorization)
        if not user_info:
            return CommonView.format_not_authorized()
        
        try:
            member_id = user_info.get("id")
            BookingModel.create_or_update_booking(
                member_id,
                booking_data.attractionId,
                booking_data.date,
                booking_data.time,
                booking_data.price
            )
            return BookingView.format_create_success()
        except Exception as e:
            return CommonView.format_error(str(e))
    
    @staticmethod
    def delete_booking(authorization):
        """刪除預定行程"""
        if not authorization:
            return CommonView.format_not_logged_in()
        
        user_info = AuthService.verify_token(authorization)
        if not user_info:
            return CommonView.format_not_authorized()
        
        try:
            member_id = user_info.get("id")
            BookingModel.delete_booking(member_id)
            return BookingView.format_delete_success()
        except Exception as e:
            return CommonView.format_error(str(e))
