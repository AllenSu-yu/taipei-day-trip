# views/booking_view.py
from views.common_view import CommonView

class BookingView:
    """處理預定行程相關的回應格式"""
    
    @staticmethod
    def format_booking_detail(booking_data):
        """格式化預定行程詳情回應"""
        data = {
            "attraction": {
                "id": booking_data["attraction_id"],
                "name": booking_data["attraction_name"],
                "address": booking_data["attraction_address"],
                "image": booking_data["attraction_image"]
            },
            "date": booking_data["date"],
            "time": booking_data["time"],
            "price": booking_data["price"]
        }
        
        return {"data": data}
    
    @staticmethod
    def format_booking_not_found():
        """格式化預定行程不存在回應"""
        return {"data": None}
    
    @staticmethod
    def format_create_success():
        """格式化建立預定行程成功回應"""
        return CommonView.format_success()
    
    @staticmethod
    def format_delete_success():
        """格式化刪除預定行程成功回應"""
        return CommonView.format_success()
