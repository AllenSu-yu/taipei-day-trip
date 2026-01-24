# models/booking_model.py
from utils.database import get_connection

class BookingModel:
    """處理預定行程相關的資料庫操作"""
    
    @staticmethod
    def get_booking_by_member_id(member_id):
        """取得會員的預定行程"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = """SELECT booking_trip_attractionid, booking_trip_date, booking_trip_time, booking_trip_price 
                     FROM booking_trip 
                     WHERE booking_trip_validflag=1 AND booking_trip_status='process' AND booking_trip_memberid=%s"""
            cursor.execute(sql, (member_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            booking_trip_attractionid = result[0]
            booking_trip_date = result[1]
            booking_trip_time = result[2]
            booking_trip_price = result[3]
            
            # 取得景點資訊
            sql = """SELECT attraction.attraction_id, attraction.name, attraction.address, image.file 
                     FROM attraction 
                     JOIN image ON attraction.attraction_id = image.attraction_id 
                     WHERE attraction.attraction_id=%s 
                     ORDER BY attraction.attraction_id ASC LIMIT 1"""
            cursor.execute(sql, (booking_trip_attractionid,))
            attraction_result = cursor.fetchone()
            
            if not attraction_result:
                return None
            
            return {
                "attraction_id": booking_trip_attractionid,
                "attraction_name": attraction_result[1],
                "attraction_address": attraction_result[2],
                "attraction_image": attraction_result[3],
                "date": booking_trip_date,
                "time": booking_trip_time,
                "price": booking_trip_price
            }
            
        except Exception as e:
            raise Exception(f"查詢失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def create_or_update_booking(member_id, attraction_id, date, time, price):
        """建立或更新預定行程"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 檢查是否已有預定行程
            sql = "SELECT * FROM booking_trip WHERE booking_trip_memberid=%s AND booking_trip_validflag=1"
            cursor.execute(sql, (member_id,))
            result = cursor.fetchone()
            
            if not result:
                # 建立新的預定行程
                sql = """INSERT INTO booking_trip(booking_trip_memberid, booking_trip_attractionid, 
                         booking_trip_date, booking_trip_time, booking_trip_price) 
                         VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (member_id, attraction_id, date, time, price))
            else:
                # 更新現有預定行程
                sql = """UPDATE booking_trip 
                         SET booking_trip_attractionid=%s, booking_trip_date=%s, booking_trip_time=%s, 
                             booking_trip_price=%s, booking_trip_status='process' 
                         WHERE booking_trip_memberid=%s"""
                cursor.execute(sql, (attraction_id, date, time, price, member_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"操作失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def delete_booking(member_id):
        """刪除預定行程"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = "UPDATE booking_trip SET booking_trip_status='deleted' WHERE booking_trip_memberid=%s"
            cursor.execute(sql, (member_id,))
            conn.commit()
            
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"刪除失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_booking_id_by_member_id(member_id):
        """取得預定行程 ID"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = """SELECT booking_trip_id FROM booking_trip 
                     WHERE booking_trip_memberid=%s AND booking_trip_validflag=1 AND booking_trip_status='process'"""
            cursor.execute(sql, (member_id,))
            result = cursor.fetchone()
            
            return result[0] if result else None
            
        except Exception as e:
            raise Exception(f"查詢失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def update_booking_status_to_completed(booking_trip_id):
        """將預定行程狀態更新為 completed"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = "UPDATE booking_trip SET booking_trip_status='completed' WHERE booking_trip_id=%s"
            cursor.execute(sql, (booking_trip_id,))
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
