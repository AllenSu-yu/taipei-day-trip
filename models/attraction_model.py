# models/attraction_model.py
from utils.database import get_connection

class AttractionModel:
    """處理景點相關的資料庫操作"""
    
    @staticmethod
    def get_attractions(page, category=None, keyword=None):
        """
        取得景點列表
        Returns: (attractions_data, images_dict, next_page)
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 處理搜尋參數
            if category:
                category = category.strip('"\'')
            if keyword:
                keyword = keyword.strip('"\'')
                MRT = keyword
                name = f"%{keyword}%"
            
            attraction_in_page = 8
            offset = attraction_in_page * page
            
            # 根據條件組裝 SQL
            if category and keyword:
                sql = """SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude 
                         FROM attraction 
                         WHERE CAT=%s AND (MRT=%s OR name LIKE %s) 
                         ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"""
                cursor.execute(sql, (category, MRT, name, offset))
                search_data = cursor.fetchall()
                
                count_sql = "SELECT COUNT(*) FROM attraction WHERE CAT=%s AND (MRT=%s OR name LIKE %s)"
                cursor.execute(count_sql, (category, MRT, name))
            elif category:
                sql = """SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude 
                         FROM attraction 
                         WHERE CAT=%s 
                         ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"""
                cursor.execute(sql, (category, offset))
                search_data = cursor.fetchall()
                
                count_sql = "SELECT COUNT(*) FROM attraction WHERE CAT=%s"
                cursor.execute(count_sql, (category,))
            elif keyword:
                sql = """SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude 
                         FROM attraction 
                         WHERE (MRT=%s OR name LIKE %s) 
                         ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"""
                cursor.execute(sql, (MRT, name, offset))
                search_data = cursor.fetchall()
                
                count_sql = "SELECT COUNT(*) FROM attraction WHERE (MRT=%s OR name LIKE %s)"
                cursor.execute(count_sql, (MRT, name))
            else:
                sql = """SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude 
                         FROM attraction 
                         ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"""
                cursor.execute(sql, (offset,))
                search_data = cursor.fetchall()
                
                count_sql = "SELECT COUNT(*) FROM attraction"
                cursor.execute(count_sql)
            
            # 計算總頁數
            all_count = cursor.fetchone()[0]
            if all_count % attraction_in_page == 0:
                all_pages = all_count // attraction_in_page
                if all_pages == 0:
                    all_pages = 1
            else:
                all_pages = all_count // attraction_in_page + 1
            
            # 計算下一頁
            if page >= all_pages - 1:
                next_page = None
            elif page >= 0:
                next_page = page + 1
            else:
                next_page = None
            
            # 取得圖片
            ids = [i[0] for i in search_data]
            images_dict = {}
            if ids:
                placeholders = ','.join(['%s'] * len(ids))
                sql = f"""SELECT attraction_id,file FROM image 
                          WHERE attraction_id IN ({placeholders}) 
                          ORDER BY attraction_id ASC"""
                cursor.execute(sql, tuple(ids))
                search_image = cursor.fetchall()
                
                for img in search_image:
                    if img[0] not in images_dict:
                        images_dict[img[0]] = []
                    images_dict[img[0]].append(img[1])
            
            return search_data, images_dict, next_page
            
        except Exception as e:
            raise Exception(f"查詢失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_attraction_by_id(attraction_id):
        """根據 ID 取得單一景點"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = """SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude 
                     FROM attraction 
                     WHERE attraction_id=%s"""
            cursor.execute(sql, (attraction_id,))
            attraction = cursor.fetchone()
            
            if not attraction:
                return None
            
            # 取得圖片
            sql = "SELECT file FROM image WHERE attraction_id=%s ORDER BY attraction_id ASC"
            cursor.execute(sql, (attraction_id,))
            images = [row[0] for row in cursor.fetchall()]
            
            return attraction, images
            
        except Exception as e:
            raise Exception(f"查詢失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_categories():
        """取得所有分類"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = "SELECT DISTINCT CAT FROM attraction"
            cursor.execute(sql)
            categories = [row[0] for row in cursor.fetchall()]
            
            return categories
            
        except Exception as e:
            raise Exception(f"查詢失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def get_mrts():
        """取得所有捷運站（依出現次數排序）"""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = """SELECT MRT, COUNT(*) AS 出現次數 
                     FROM attraction 
                     WHERE MRT IS NOT NULL 
                     GROUP BY MRT 
                     ORDER BY 出現次數 DESC"""
            cursor.execute(sql)
            mrts = [row[0] for row in cursor.fetchall()]
            
            return mrts
            
        except Exception as e:
            raise Exception(f"查詢失敗: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
