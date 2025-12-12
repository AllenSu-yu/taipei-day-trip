import json
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
load_dotenv()  # 載入 .env 檔案


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
	# 從連線池取出一個連線
	return cnxpool.get_connection()

conn = get_connection()
cursor = conn.cursor()

with open("data/taipei-attractions.json", "r", encoding="utf-8") as f:
    data = json.load(f)
results = data["result"]["results"]

# 定義欄位順序
fields = ["_id", "name", "CAT", "MRT", "rate", "direction", "date", 
            "longitude", "REF_WP", "avBegin", "langinfo", "SERIAL_NO", 
            "RowNumber", "MEMO_TIME", "POI", "idpt", "latitude", 
            "description", "avEnd", "address"]
placeholder_values= ",".join(["%s"] * 20)
sql = f"INSERT INTO attraction (attraction_id,name,CAT,MRT,rate,direction,date,longitude,REF_WP,avBegin,langinfo,SERIAL_NO,RowNumber,MEMO_TIME,POI,idpt,latitude,description,avEnd,address) VALUES ({placeholder_values})"


for i in results:
    values = tuple(i.get(field) for field in fields) 
    cursor.execute(sql, values)

conn.commit()
print("執行成功")

cursor.close()
conn.close()

