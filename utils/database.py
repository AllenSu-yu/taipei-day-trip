# utils/database.py
import os
import time
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

dbconfig = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "taipeitrip")
}

# 建立全域連線池
try:
    cnxpool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        pool_reset_session=True,
        autocommit=False,
        **dbconfig
    )
except Exception as e:
    raise RuntimeError(f"無法建立資料庫連線池:{e}")

def get_connection():
    """
    從連線池取出一個連線，並確保連線有效
    包含連線健康檢查和自動重試機制
    """
    max_retries = 5
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        conn = None
        try:
            conn = cnxpool.get_connection()
            
            if not conn.is_connected():
                print(f"嘗試 {attempt + 1}: 連線失效，重新取得...")
                try:
                    conn.close()
                except:
                    pass
                conn = None
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise RuntimeError("無法取得有效的資料庫連線")
            
            return conn

        except Exception as e:
            if conn:
                try:
                    conn.close()
                except:
                    pass
            conn = None
            
            if attempt == max_retries - 1:
                raise RuntimeError(f"無法取得連線: {e}")
            
            time.sleep(retry_delay)
            continue
    
    raise RuntimeError("無法取得有效的資料庫連線")
