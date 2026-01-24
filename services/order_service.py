# services/order_service.py
import random
import datetime

class OrderService:
    """處理訂單相關的業務邏輯"""
    
    @staticmethod
    def create_order_number():
        """產生訂單編號"""
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d%H%M%S")
        random_num = random.randint(100, 999)
        orders_number = f"{date_str}{random_num}"
        return orders_number
