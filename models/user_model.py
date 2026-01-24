# models/user_model.py
from utils.database import get_connection

class UserModel:
    """處理使用者相關的資料庫操作"""
    
    @staticmethod
    def create_user(name, email, password):
        """建立新使用者"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 檢查 email 是否已存在
            sql = "SELECT email FROM member WHERE email=%s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            
            if result:
                return False, "註冊失敗，Email已使用"
            
            # 插入新使用者
            sql = "INSERT INTO member(name,email,password) VALUES(%s,%s,%s)"
            cursor.execute(sql, (name, email, password))
            conn.commit()
            
            return True, None
            
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"註冊失敗:{str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_user_by_credentials(email, password):
        """根據 email 和 password 取得使用者"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = "SELECT id, name, email FROM member WHERE email=%s AND password=%s"
            cursor.execute(sql, (email, password))
            result = cursor.fetchone()
            
            return result
            
        except Exception as e:
            raise Exception(f"查詢失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
