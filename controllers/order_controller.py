# controllers/order_controller.py
from models.order_model import OrderModel
from models.booking_model import BookingModel
from services.auth_service import AuthService
from services.payment_service import PaymentService
from services.order_service import OrderService
from views.order_view import OrderView
from views.common_view import CommonView

class OrderController:
    """處理訂單相關的請求"""
    
    @staticmethod
    def create_order(orders_data, authorization):
        """建立訂單"""
        if not authorization:
            return CommonView.format_not_logged_in()
        
        user_info = AuthService.verify_token(authorization)
        if not user_info:
            return CommonView.format_not_authorized()
        
        try:
            member_id = user_info.get("id")
            
            # 取得預定行程 ID
            booking_trip_id = BookingModel.get_booking_id_by_member_id(member_id)
            if not booking_trip_id:
                return OrderView.format_booking_not_found_error()
            
            # 產生訂單編號
            order_number = OrderService.create_order_number()
            
            # 準備訂單資料
            order_data = {
                'order_number': order_number,
                'booking_trip_id': booking_trip_id,
                'member_id': member_id,
                'price': orders_data.order.price,
                'attraction_id': orders_data.order.trip.attraction.id,
                'attraction_name': orders_data.order.trip.attraction.name,
                'attraction_address': orders_data.order.trip.attraction.address,
                'attraction_image': orders_data.order.trip.attraction.image,
                'date': orders_data.order.trip.date,
                'time': orders_data.order.trip.time,
                'contact_name': orders_data.order.contact.name,
                'contact_email': orders_data.order.contact.email,
                'contact_phone': orders_data.order.contact.phone
            }
            
            # 建立訂單
            OrderModel.create_order(order_data)
            
            # 呼叫 TapPay 付款
            payment_status, payment_response = PaymentService.tappay_payment(
                orders_data.prime,
                orders_data.order.price,
                orders_data.order.contact.phone,
                orders_data.order.contact.name,
                orders_data.order.contact.email
            )
            
            # 判斷付款是否成功
            is_payment_success = (payment_status == 200 and payment_response.get("status") == 0)
            
            if is_payment_success:
                # 更新訂單狀態為已付款
                OrderModel.update_order_payment_status(order_number, 'PAID')
                # 更新預定行程狀態為已完成
                BookingModel.update_booking_status_to_completed(booking_trip_id)
                payment_message = "付款成功"
            else:
                payment_message = payment_response.get("msg", "付款失敗")
            
            return OrderView.format_create_order_success(
                order_number,
                payment_response.get("status", -1),
                payment_message
            )
            
        except Exception as e:
            error_message = "建立訂單失敗"
            error_str = str(e).lower()
            if "booking_trip" in error_str:
                error_message = "找不到預定行程，請先預定行程"
            elif "foreign key" in error_str:
                error_message = "資料驗證失敗，請檢查輸入資料"
            elif "not null" in error_str:
                error_message = "請填寫所有必填欄位"
            
            return OrderView.format_create_order_error(error_message)
    
    @staticmethod
    def get_order(order_number, authorization):
        """取得訂單資訊"""
        if not authorization:
            return CommonView.format_not_logged_in()
        
        user_info = AuthService.verify_token(authorization)
        if not user_info:
            return CommonView.format_not_authorized()
        
        try:
            member_id = user_info.get("id")
            result = OrderModel.get_order_by_number(order_number, member_id)
            
            if not result:
                return OrderView.format_order_not_found()
            
            status = 1 if result['order_payment_status'] == 'PAID' else 0
            
            return OrderView.format_order_detail(order_number, result, status)
            
        except Exception as e:
            return CommonView.format_error("訂單查詢失敗")
