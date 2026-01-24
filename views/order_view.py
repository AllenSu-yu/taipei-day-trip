# views/order_view.py
from views.common_view import CommonView

class OrderView:
    """處理訂單相關的回應格式"""
    
    @staticmethod
    def format_create_order_success(order_number, payment_status, payment_message):
        """格式化建立訂單成功回應"""
        return {
            "data": {
                "number": order_number,
                "payment": {
                    "status": payment_status,
                    "message": payment_message
                }
            }
        }
    
    @staticmethod
    def format_order_detail(order_number, order_data, status):
        """格式化訂單詳情回應"""
        return {
            "data": {
                "number": order_number,
                "price": order_data['order_price'],
                "trip": {
                    "attraction": {
                        "id": order_data['order_attraction_id'],
                        "name": order_data['order_attraction_name'],
                        "address": order_data['order_attraction_address'],
                        "image": order_data['order_attraction_image']
                    },
                    "date": str(order_data['order_date']),
                    "time": order_data['order_time']
                },
                "contact": {
                    "name": order_data['order_contact_name'],
                    "email": order_data['order_contact_email'],
                    "phone": order_data['order_contact_phone']
                },
                "status": status
            }
        }
    
    @staticmethod
    def format_order_not_found():
        """格式化訂單不存在回應"""
        return {"data": None}
    
    @staticmethod
    def format_booking_not_found_error():
        """格式化找不到預定行程錯誤回應"""
        return CommonView.format_error("找不到預定行程，請先預定行程")
    
    @staticmethod
    def format_create_order_error(error_message):
        """格式化建立訂單錯誤回應"""
        return CommonView.format_error(error_message)
