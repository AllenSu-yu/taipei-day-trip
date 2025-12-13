from fastapi import *
from fastapi.responses import FileResponse
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
load_dotenv()  # 載入 .env 檔案
app=FastAPI()

dbconfig = {
	"host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "taipeitrip")
}


#建立全域連線池
cnxpool = pooling.MySQLConnectionPool(
	pool_name="mypool",
	pool_size=5,
	**dbconfig
)

def get_connection():
	"""從連線池取出一個連線"""
	return cnxpool.get_connection()


@app.get("/api/attractions")
async def get_attractions(request:Request, page:int = Query(...,ge=0), category:str = Query(None), keyword:str = Query(None)):
	conn = get_connection()
	cursor = conn.cursor()
	
	#計算總共有幾頁
	sql = "SELECT COUNT(*) FROM attraction"
	cursor.execute(sql)
	all_count=cursor.fetchone()[0]
	all_pages=0
	attraction_in_page = 8
	if all_count%attraction_in_page ==0:
		all_pages = all_count/attraction_in_page
	else:
		all_pages = all_count//attraction_in_page+1
		
	if page >= all_pages-1:
		nextPage = None
	elif page>=0:
		nextPage = page+1
	
		
	offset = attraction_in_page *(page)
	

	#組裝回傳的data
	if category:
		category=category.strip('"\'')
	if keyword:
		keyword=keyword.strip('"\'')
		MRT=keyword
		name=f"%{keyword}%"

	if category and keyword:
		sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction WHERE CAT= %s AND (MRT = %s OR name like %s)  ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"
		cursor.execute(sql,(category,MRT,name,offset))
	elif category:
		sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction WHERE CAT= %s  ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"
		cursor.execute(sql,(category,offset))

	elif keyword:
		sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction WHERE (MRT = %s OR name like %s)  ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"
		cursor.execute(sql,(MRT,name,offset))	
	
	else:
		sql = "SELECT attraction_id,name,CAT,description,address,direction,MRT,latitude,longitude FROM attraction ORDER BY attraction_id ASC LIMIT 8 OFFSET %s"
		cursor.execute(sql,(offset, ))
	search_data = cursor.fetchall()
	
	##找出所有的attraction_id
	ids = []
	for i in search_data:
		attraction_id = i[0]
		ids.append(attraction_id)

	if ids:
		sql = f"SELECT attraction_id,file FROM image WHERE attraction_id in {tuple(ids)} ORDER BY attraction_id ASC"
		cursor.execute(sql)
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
async def get_categories(request:Request):
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