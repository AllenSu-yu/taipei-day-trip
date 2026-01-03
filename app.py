from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles# 在 app = FastAPI() 之後加入
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
import datetime
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, EmailStr

load_dotenv()  # 載入 .env 檔案
app=FastAPI()
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/image", StaticFiles(directory="image"), name="image")
app.mount("/components", StaticFiles(directory="components"), name="components")
app.mount("/js", StaticFiles(directory="js"), name="js")

dbconfig = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD",""),
    "database": os.getenv("DB_NAME", "taipeitrip")
}


#建立全域連線池
try:
	cnxpool = pooling.MySQLConnectionPool(
		pool_name="mypool",
		pool_size=5,
		**dbconfig
	)
except Exception as e:
	raise RuntimeError(f"無法建立資料庫連線池:{e}")

def get_connection():
	"""從連線池取出一個連線"""
	try:
		return cnxpool.get_connection()
	except Exception as e:
		raise RuntimeError(f"無法從連線池取得連線:{e}")


@app.get("/api/attractions")
async def get_attractions(request:Request, page:int = Query(...,ge=0), category:str = Query(None), keyword:str = Query(None)):
	conn = get_connection()
	cursor = conn.cursor()
	

	#組裝回傳的data
	if category:
		category=category.strip('"\'')
	if keyword:
		keyword=keyword.strip('"\'')
		MRT=keyword
		name=f"%{keyword}%"

	search_data = []
	nextPage = None
	all_pages=0
	attraction_in_page = 8
	offset = attraction_in_page *(page)
	if category and keyword:
		sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction WHERE CAT= %s AND (MRT = %s OR name like %s)  ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"
		cursor.execute(sql,(category,MRT,name,offset))
		search_data = cursor.fetchall()
		#計算總共有幾頁
		sql = "SELECT COUNT(*) FROM attraction WHERE CAT= %s AND (MRT = %s OR name like %s)"
		cursor.execute(sql,(category,MRT,name))
		all_count=cursor.fetchone()[0]
		if all_count%attraction_in_page ==0:
			all_pages = all_count//attraction_in_page
			if all_pages == 0:
				all_pages = 1
		else:
			all_pages = all_count//attraction_in_page+1
			
		if page >= all_pages-1:
			nextPage = None
		elif page>=0:
			nextPage = page+1
	elif category:
		sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction WHERE CAT= %s  ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"
		cursor.execute(sql,(category,offset))
		search_data = cursor.fetchall()
		#計算總共有幾頁
		sql = "SELECT COUNT(*) FROM attraction WHERE CAT= %s"
		cursor.execute(sql,(category,))
		all_count=cursor.fetchone()[0]
		if all_count%attraction_in_page ==0:
			all_pages = all_count//attraction_in_page
			if all_pages == 0:
				all_pages = 1
		else:
			all_pages = all_count//attraction_in_page+1
			
		if page >= all_pages-1:
			nextPage = None
		elif page>=0:
			nextPage = page+1
	elif keyword:
		sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction WHERE (MRT = %s OR name like %s)  ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"
		cursor.execute(sql,(MRT,name,offset))
		search_data = cursor.fetchall()
		#計算總共有幾頁
		sql = "SELECT COUNT(*) FROM attraction WHERE (MRT = %s OR name like %s)"
		cursor.execute(sql,(MRT,name))
		all_count=cursor.fetchone()[0]
		if all_count%attraction_in_page ==0:
			all_pages = all_count//attraction_in_page
			if all_pages == 0:
				all_pages = 1
		else:
			all_pages = all_count//attraction_in_page+1
			
		if page >= all_pages-1:
			nextPage = None
		elif page>=0:
			nextPage = page+1
	
	else:
		sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"
		cursor.execute(sql,(offset, ))
		search_data = cursor.fetchall()
		#計算總共有幾頁
		sql = "SELECT COUNT(*) FROM attraction"
		cursor.execute(sql)
		all_count=cursor.fetchone()[0]
		if all_count%attraction_in_page ==0:
			all_pages = all_count//attraction_in_page
			if all_pages == 0:
				all_pages = 1
		else:
			all_pages = all_count//attraction_in_page+1
			
		if page >= all_pages-1:
			nextPage = None
		elif page>=0:
			nextPage = page+1


	##找出所有的attraction_id
	ids = []
	for i in search_data:
		attraction_id = i[0]
		ids.append(attraction_id)

	if ids:
		# 使用參數化查詢，避免 SQL 注入和語法錯誤
		placeholders = ','.join(['%s'] * len(ids))
		sql = f"SELECT attraction_id,file FROM image WHERE attraction_id IN ({placeholders}) ORDER BY attraction_id ASC"
		cursor.execute(sql, tuple(ids))
		search_image = cursor.fetchall()	
	else:
		search_image = []
	
	data = []	
	for i in search_data:
		images = []
		for image in search_image:
			if image[0] == i[0]:
				images.append(image[1])
		attraction = {
			"id": i[0],
			"name": i[1],
			"category": i[2],
			"description": i[3],
			"address": i[4],
			"transport": i[5],
			"mrt": i[6],
			"lat": i[7],
			"lng": i[8],
			"images" : images
		}
		data.append(attraction)
		
		
	response = {
		"nextPage":nextPage,
		"data": data
	}

	cursor.close()
	conn.close()
	return response

@app.get("/api/attraction/{attractionId}")
async def get_attraction_byId(request:Request,attractionId:int):
	conn = get_connection()
	cursor = conn.cursor()
	
	sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction WHERE attraction_id=%s"
	cursor.execute(sql, (attractionId,))
	search_data = cursor.fetchall()
	if search_data:
		attraction = search_data[0]
	else:
		error_message = {
			"error":True,
			"message":"景點編號不正確"
		}
		cursor.close()
		conn.close()
		return error_message

	sql = "SELECT attraction_id,file FROM image WHERE attraction_id = %s ORDER BY attraction_id ASC"
	cursor.execute(sql, (attractionId,))
	search_image = cursor.fetchall()	

	images = []
	for image in search_image:
		if image[0] == attractionId:
			images.append(image[1])
	data = {
		"id": attraction[0],
		"name": attraction[1],
		"category": attraction[2],
		"description": attraction[3],
		"address": attraction[4],
		"transport": attraction[5],
		"mrt": attraction[6],
		"lat": attraction[7],
		"lng": attraction[8],
		"images" : images
	}

	
	response = {
		"data": data
	}

	cursor.close()
	conn.close()
	return response

@app.get("/api/categories")
async def get_categories(request:Request):
	conn = get_connection()
	cursor = conn.cursor()

	sql = "SELECT DISTINCT CAT FROM attraction"
	cursor.execute(sql)
	search_data = cursor.fetchall()
	
	data = []
	for i in search_data:
		data.append(i[0])

	response = {
		"data":data
	}

	cursor.close()
	conn.close()
	return response

@app.get("/api/mrts")
async def get_mrts(request:Request):
	conn = get_connection()
	cursor = conn.cursor()

	sql = "SELECT MRT, COUNT(*) AS 出現次數 FROM attraction WHERE MRT IS NOT NULL GROUP BY MRT ORDER BY 出現次數 DESC"
	cursor.execute(sql)
	search_data = cursor.fetchall()
	
	data = []
	for i in search_data:
		data.append(i[0])

	response = {
		"data":data
	}

	cursor.close()
	conn.close()
	return response



#註冊會員
class UserSignUpInput(BaseModel):
	name:str
	email:EmailStr # 自動驗證 email 格式
	password:str

@app.post("/api/user")
async def signup(user_data: UserSignUpInput):
	conn = None
	cursor = None
	try:	
		conn = get_connection()
		cursor = conn.cursor()

		# 檢查 email 是否已存在
		sql = "SELECT email FROM member WHERE email=%s"
		cursor.execute(sql, (user_data.email,))
		result = cursor.fetchone()
		
		if result is None:
			# 插入新使用者
			sql = "INSERT INTO member(name,email,password) VALUES(%s,%s,%s)"
			cursor.execute(sql,(user_data.name,user_data.email,user_data.password))
			conn.commit()
			return {"ok": True}
		else:
			return {
				"error": True,
				"message":"註冊失敗，Email已使用"			
			}
	except Exception as e:
		if conn:
			conn.rollback()
		return {
			"error": True,
			"message":f"註冊失敗:{str(e)}"
		}
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()



#使用者登入
#將使用者資訊換成token
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY 環境變數未設定")

def create_token(user):
    # 支援元組和物件兩種格式
    try:
        if isinstance(user, tuple):
            if len(user) < 3:
                raise ValueError("元組長度不足，需要至少 3 個元素")
            user_id, user_name, user_email = user[0], user[1], user[2]
        else:
            user_id = user.id
            user_name = user.name
            user_email = user.email
    except (IndexError, AttributeError) as e:
        raise ValueError(f"無法從 user 物件取得必要資訊: {e}")
    
    payload = {
        "id": user_id,
        "name": user_name,
        "email": user_email,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

#驗證 Token (放在每個需要授權的 API 中)
def verify_token(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    parts = auth_header.split(" ", 1)  # 最多分割一次
    if len(parts) != 2 or not parts[1]:
        return None
    token = parts[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except InvalidTokenError:
        return None

#建立一個登入route
class UserLoginInput(BaseModel):
	email:EmailStr
	password:str

@app.put("/api/user/auth")
async def login(login_data: UserLoginInput):
	conn = None
	cursor = None
	try:
		conn = get_connection()
		cursor = conn.cursor()
			
		sql = "SELECT id, name, email FROM member WHERE email=%s AND password=%s"
		cursor.execute(sql, (login_data.email, login_data.password))
		result = cursor.fetchone()
		if result:
			return {"token": create_token(result)}
		else:
			return {
				"error": True,
				"message": "帳號不存在或密碼錯誤"
			}
	except Exception as e:
		if conn:
			conn.rollback()
		return {
			"error": True,
			"message": f"登入失敗: {str(e)}"
		}

	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()

#建立一個驗證登入狀態的route
@app.get("/api/user/auth")
async def check_auth(authorization: str = Header(None, alias="Authorization")):
	if not authorization:
		return {"data": None} 
	user_info = verify_token(authorization)
	if user_info:
		return {
			"data": {
				"id": user_info.get("id"),
				"name": user_info.get("name"),
				"email": user_info.get("email")
			}
		}
	return {"data": None} 



# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

