# models/order_model.py
from utils.database import get_connection

class OrderModel:
    """處理訂單相關的資料庫操作"""
    
    @staticmethod
    def create_order(order_data):
        """建立訂單"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = """INSERT INTO orders(order_number, order_booking_trip_id, order_member_id, order_price, 
                     order_attraction_id, order_attraction_name, order_attraction_address, order_attraction_image, 
                     order_date, order_time, order_contact_name, order_contact_email, order_contact_phone) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(sql, (
                order_data['order_number'],
                order_data['booking_trip_id'],
                order_data['member_id'],
                order_data['price'],
                order_data['attraction_id'],
                order_data['attraction_name'],
                order_data['attraction_address'],
                order_data['attraction_image'],
                order_data['date'],
                order_data['time'],
                order_data['contact_name'],
                order_data['contact_email'],
                order_data['contact_phone']
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"建立訂單失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def update_order_payment_status(order_number, status):
        """更新訂單付款狀態"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = "UPDATE orders SET order_payment_status=%s WHERE order_number=%s"
            cursor.execute(sql, (status, order_number))
            conn.commit()
            
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"更新失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_order_by_number(order_number, member_id):
        """根據訂單編號取得訂單"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """SELECT order_payment_status, order_price, order_attraction_id, 
                     order_attraction_name, order_attraction_address, order_attraction_image, 
                     order_date, order_time, order_contact_name, order_contact_email, order_contact_phone 
                     FROM orders 
                     WHERE order_number=%s AND order_member_id=%s AND order_validflag=1"""
            cursor.execute(sql, (order_number, member_id))
            result = cursor.fetchone()
            
            return result
            
        except Exception as e:
            raise Exception(f"查詢失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
