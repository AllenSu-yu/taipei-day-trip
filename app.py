import random
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
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
import requests
import json

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

#取得尚未確認下單的預定行程
@app.get("/api/booking")
async def get_bookingtrip(authorization:str = Header(None, alias="Authorization")):
	#確認是否有登入的token
	if not authorization:
		return {
			"error":True,
			"message":"尚未登入"
		}
	#驗證token是否正確
	user_info = verify_token(authorization)
	if not user_info:
		return {"error": True, "message": "未授權"}

	conn = None
	cursor = None
	try: 
		conn = get_connection()
		cursor = conn.cursor()
		member_id = user_info.get("id")		
		#搜尋booking_trip表格，確認是否有status = process的待預定行程
		sql = "SELECT booking_trip_attractionid, booking_trip_date, booking_trip_time, booking_trip_price FROM booking_trip WHERE booking_trip_validflag= 1 AND booking_trip_status='process' AND booking_trip_memberid=%s"
		cursor.execute(sql, (member_id,))
		result = cursor.fetchone()
		if result:
			booking_trip_attractionid = result[0]
			booking_trip_date = result[1]
			booking_trip_time = result[2]
			booking_trip_price = result[3]
			sql = "SELECT attraction.attraction_id, attraction.name, attraction.address, image.file FROM attraction JOIN image ON attraction.attraction_id = image.attraction_id WHERE attraction.attraction_id=%s ORDER BY attraction.attraction_id ASC LIMIT 1"
			cursor.execute(sql, (booking_trip_attractionid,))
			result = cursor.fetchone()
			if result:
				attraction_name = result[1]
				attraction_address = result[2]
				attraction_image = result[3]

				data = {
						"attraction": {
							"id": booking_trip_attractionid,
							"name": attraction_name,
							"address": attraction_address,
							"image": attraction_image
						},
						"date": booking_trip_date,
						"time": booking_trip_time,
						"price": booking_trip_price
					}


				return {"data": data}
			else:
				return {
					"data": None
				}
		else:
			return {
				"data": None
			}
	except Exception as e:
		if conn:
			conn.rollback()
		return {
			"error": True,
			"message": "登入失敗"
		}
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()

#建立新的預定行程(新增一個booking_trip將booking_trip_status設成'process')
# 定義請求模型
class BookingTripInput(BaseModel):
    attractionId: int = Field(..., gt=0, description="景點ID必須大於0")
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="日期格式：YYYY-MM-DD")
    time: Literal["morning", "afternoon"] = Field(..., description="時間：morning 或 afternoon")
    price: Literal[2000, 2500] = Field(..., description="價格：2000 或 2500")


@app.post("/api/booking")
async def create_bookingtrip(booking_data: BookingTripInput, authorization:str = Header(None, alias="Authorization")):
	if not authorization:
		return {"error":True, "message":"尚未登入" }

	user_info = verify_token(authorization)
	if not user_info:
		return {"error": True, "message": "未授權"}

	conn = None
	cursor = None
	try: 
		conn = get_connection()
		cursor = conn.cursor()
		member_id = user_info.get("id")
		sql ="SELECT * FROM booking_trip WHERE booking_trip_memberid=%s AND booking_trip_validflag = 1"
		cursor.execute(sql,(member_id,))
		result = cursor.fetchone()

		if not result:
			sql="INSERT INTO booking_trip(booking_trip_memberid, booking_trip_attractionid, booking_trip_date, booking_trip_time, booking_trip_price) VALUES (%s, %s, %s, %s, %s)"
			cursor.execute(sql,(member_id, booking_data.attractionId, booking_data.date, booking_data.time, booking_data.price))
			conn.commit()
			return {"ok": True}
		
		else:
			sql="UPDATE booking_trip SET booking_trip_attractionid=%s, booking_trip_date=%s, booking_trip_time=%s, booking_trip_price=%s, booking_trip_status='process' WHERE booking_trip_memberid=%s"
			cursor.execute(sql,(booking_data.attractionId, booking_data.date, booking_data.time, booking_data.price, member_id))
			conn.commit()
			return {"ok": True}
		
	except Exception as e:
		if conn:
			conn.rollback()
		return {
			"error": True,
			"message": "登入失敗"
		}
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()

#刪除目前的預定行程 (將booking_trip_status設成'deleted')
@app.delete("/api/booking")
async def delete_bookingtrip(authorization:str = Header(None, alias="Authorization")):
	if not authorization:
		return {"error":True, "message":"尚未登入" }

	user_info = verify_token(authorization)
	if not user_info:
		return {"error": True, "message": "未授權"}

	conn = None
	cursor = None
	try: 
		conn = get_connection()
		cursor = conn.cursor()
		member_id = user_info.get("id")
		sql = "UPDATE booking_trip SET booking_trip_status='deleted' WHERE booking_trip_memberid=%s"
		cursor.execute(sql, (member_id,))
		conn.commit()
		return {"ok": True}

	except Exception as e:
		if conn:
			conn.rollback()
		return {
			"error": True,
			"message": "登入失敗"
		}
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()

# 打去tappay完成付款
def tappay_payment(prime,amount,phone_number,name,email):
	# API URL (測試環境 )
	url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"

	# Header
	headers = {
		"Content-Type": "application/json",
		"x-api-key": os.getenv("x-api-key")  # 這裡放 Partner Key
	}

	# Body
	payload = {
		"prime": prime,       # 前端 SDK 取得的 prime
		"partner_key": os.getenv("x-api-key"),   # 與 Header 一致
		"merchant_id": "tppf_allensu_GP_POS_3",        # TapPay 後台設定的商店代號
		"details": "TapPay Test",
		"amount": amount,
		"cardholder": {
			"phone_number": phone_number,
			"name": name,
			"email": email
		}
	}

	# 發送 POST 請求
	response = requests.post(url, headers=headers, data=json.dumps(payload))

	# 檢查回應
	print("Status Code:", response.status_code)
	response_data = response.json()
	print("Response Body:", response_data)
	
	# 回傳狀態碼和回應內容
	return response.status_code, response_data


# 產生訂單編號邏輯
def create_orders_number():
	# 日期+時分秒+隨機數字三位數
	now = datetime.datetime.now()
	date_str = now.strftime("%Y%m%d%H%M%S")
	random_num = random.randint(100, 999)  # 三位數隨機數字
	orders_number = f"{date_str}{random_num}"
	return orders_number




#建立新的訂單
# 定義請求模型
class AttractionInput(BaseModel):
	id: int = Field(..., gt=0, description="景點ID必須大於0")
	name: str
	address: str
	image: str

class TripInput(BaseModel):
	attraction: AttractionInput
	date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="日期格式：YYYY-MM-DD")
	time: Literal["morning", "afternoon"] = Field(..., description="時間：morning 或 afternoon")

class ContactInput(BaseModel):
	name: str
	email: EmailStr
	phone: str

class OrderInput(BaseModel):
	price: Literal[2000, 2500] = Field(..., description="價格：2000 或 2500")
	trip: TripInput
	contact: ContactInput

class CreateOrdersInput(BaseModel):
	prime: str
	order: OrderInput

@app.post("/api/orders")
async def create_orders(orders_data: CreateOrdersInput, authorization: str = Header(None, alias="Authorization")):
	if not authorization:
		return {"error":True, "message":"尚未登入" }

	user_info = verify_token(authorization)
	if not user_info:
		return {"error": True, "message": "未授權"}
	
	# 存取嵌套資料範例：
	# prime = orders_data.prime
	# price = orders_data.order.price
	# attraction_id = orders_data.order.trip.attraction.id
	# attraction_name = orders_data.order.trip.attraction.name
	# attraction_address = orders_data.order.trip.attraction.address
	# attraction_image = orders_data.order.trip.attraction.image
	# date = orders_data.order.trip.date
	# time = orders_data.order.trip.time
	# contact_name = orders_data.order.contact.name
	# contact_email = orders_data.order.contact.email
	# contact_phone = orders_data.order.contact.phone
	
	conn = None
	cursor = None
	try: 
		conn = get_connection()
		cursor = conn.cursor()
		
		sql = "INSERT INTO orders(order_number, order_booking_trip_id, order_member_id, order_price, order_attraction_id, order_attraction_name, order_attraction_address, order_attraction_image, order_date, order_time, order_contact_name, order_contact_email, order_contact_phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		member_id = user_info.get("id")
		order_number = create_orders_number()
		
		# 取得 booking_trip_id
		sql_booking = "SELECT booking_trip_id FROM booking_trip WHERE booking_trip_memberid=%s AND booking_trip_validflag = 1 AND booking_trip_status='process'"
		cursor.execute(sql_booking, (member_id,))
		booking_result = cursor.fetchone()
		booking_trip_id = booking_result[0] if booking_result else None

		# 建立訂單
		cursor.execute(sql, (
			order_number,
			booking_trip_id,
			member_id,
			orders_data.order.price,
			orders_data.order.trip.attraction.id,
			orders_data.order.trip.attraction.name,
			orders_data.order.trip.attraction.address,
			orders_data.order.trip.attraction.image,
			orders_data.order.trip.date,
			orders_data.order.trip.time,
			orders_data.order.contact.name,
			orders_data.order.contact.email,
			orders_data.order.contact.phone,
		))

		# 打去TapPay付款
		payment_status, payment_response = tappay_payment(
			orders_data.prime,
			orders_data.order.price,
			orders_data.order.contact.phone,
			orders_data.order.contact.name,
			orders_data.order.contact.email
		)

		# 判斷付款是否成功（HTTP 200 且回應中的 status 為 0）
		is_payment_success = (payment_status == 200 and payment_response.get("status") == 0)
		
		if is_payment_success:
			# 如果付款成功，將order_payment_status狀態更新為paid，將booking_trip_status更新為completed
			sql_update_order = "UPDATE orders SET order_payment_status = 'PAID' WHERE order_number = %s"
			cursor.execute(sql_update_order, (order_number,))

			# 更新預定行程狀態為 completed
			if booking_trip_id:
				sql_update_booking = "UPDATE booking_trip SET booking_trip_status = 'completed' WHERE booking_trip_id = %s"
				cursor.execute(sql_update_booking, (booking_trip_id,))
			
			payment_message = "付款成功"
		else:
			# 付款失敗，訂單狀態保持 UNPAID
			payment_message = payment_response.get("msg", "付款失敗")

		conn.commit()
		
		# 回傳訂單建立成功，包含付款狀態
		return {
			"data": {
				"number": order_number,
				"payment": {
					"status": payment_response.get("status", -1),
					"message": payment_message
				}
			}
		}
		
	except Exception as e:
		if conn:
			conn.rollback()
		# 根據不同錯誤情境回傳對應訊息
		error_message = "建立訂單失敗"
		if "booking_trip" in str(e).lower():
			error_message = "找不到預定行程，請先預定行程"
		elif "foreign key" in str(e).lower():
			error_message = "資料驗證失敗，請檢查輸入資料"
		elif "not null" in str(e).lower():
			error_message = "請填寫所有必填欄位"
		
		return {
			"error": True,
			"message": error_message
		}
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()


@app.get("/api/order/{orderNumber}")
async def get_orders(orderNumber:str, authorization:str = Header(None, alias="Authorization")):
	if not authorization:
		return {"error":True, "message":"尚未登入" }

	user_info = verify_token(authorization)
	if not user_info:
		return {"error": True, "message": "未授權"}

	conn = None
	cursor = None
	try: 
		conn = get_connection()
		cursor = conn.cursor(dictionary=True)
		member_id = user_info.get("id")
		sql = """
			SELECT 	order_payment_status, order_price, order_attraction_id, 
					order_attraction_name, order_attraction_address, order_attraction_image, 
					order_date, order_time, order_contact_name, order_contact_email, order_contact_phone 
			FROM orders 
			WHERE order_number=%s AND order_member_id=%s AND order_validflag=1
		"""
		cursor.execute(sql, (orderNumber, member_id))
		result=cursor.fetchone()

		if not result:  # 先檢查 result 是否存在
			return {"data":None}
		
		if result['order_payment_status'] == 'PAID':
			status = 1
		else: status = 0
		
		if result:
			order_detail = {
				"data": {
					"number": orderNumber,
					"price": result['order_price'],
					"trip": {
						"attraction": {
							"id": result['order_attraction_id'],
							"name": result['order_attraction_name'],
							"address": result['order_attraction_address'],
							"image": result['order_attraction_image']
						},
						"date": str(result['order_date']),  # 轉換為字串格式
						"time": result['order_time']
					},
					"contact": {
						"name": result['order_contact_name'],
						"email": result['order_contact_email'],
						"phone": result['order_contact_phone']
					},
					"status": status
				}
			}
			return order_detail
		else:
			return {"data":None}

	except Exception as e:
		return {
			"error": True,
			"message": "訂單查詢失敗"
		}
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()	














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

