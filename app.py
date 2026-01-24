# app.py
from fastapi import FastAPI, Request, Query, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

# 匯入 Controllers
from controllers.attraction_controller import AttractionController
from controllers.user_controller import UserController
from controllers.booking_controller import BookingController
from controllers.order_controller import OrderController

app = FastAPI()

# 靜態檔案
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/image", StaticFiles(directory="image"), name="image")
app.mount("/components", StaticFiles(directory="components"), name="components")
app.mount("/js", StaticFiles(directory="js"), name="js")

# ========== 景點相關 API ==========
@app.get("/api/attractions")
async def get_attractions(
    request: Request,
    page: int = Query(..., ge=0),
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None)
):
    return AttractionController.get_attractions(page, category, keyword)

@app.get("/api/attraction/{attractionId}")
async def get_attraction_byId(request: Request, attractionId: int):
    return AttractionController.get_attraction_by_id(attractionId)

@app.get("/api/categories")
async def get_categories(request: Request):
    return AttractionController.get_categories()

@app.get("/api/mrts")
async def get_mrts(request: Request):
    return AttractionController.get_mrts()

# ========== 使用者相關 API ==========
class UserSignUpInput(BaseModel):
    name: str
    email: EmailStr
    password: str

@app.post("/api/user")
async def signup(user_data: UserSignUpInput):
    return UserController.signup(user_data.name, user_data.email, user_data.password)

class UserLoginInput(BaseModel):
    email: EmailStr
    password: str

@app.put("/api/user/auth")
async def login(login_data: UserLoginInput):
    return UserController.login(login_data.email, login_data.password)

@app.get("/api/user/auth")
async def check_auth(authorization: str = Header(None, alias="Authorization")):
    return UserController.check_auth(authorization)

# ========== 預定行程相關 API ==========
@app.get("/api/booking")
async def get_bookingtrip(authorization: str = Header(None, alias="Authorization")):
    return BookingController.get_booking(authorization)

class BookingTripInput(BaseModel):
    attractionId: int = Field(..., gt=0, description="景點ID必須大於0")
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="日期格式：YYYY-MM-DD")
    time: Literal["morning", "afternoon"] = Field(..., description="時間：morning 或 afternoon")
    price: Literal[2000, 2500] = Field(..., description="價格：2000 或 2500")

@app.post("/api/booking")
async def create_bookingtrip(
    booking_data: BookingTripInput,
    authorization: str = Header(None, alias="Authorization")
):
    return BookingController.create_booking(booking_data, authorization)

@app.delete("/api/booking")
async def delete_bookingtrip(authorization: str = Header(None, alias="Authorization")):
    return BookingController.delete_booking(authorization)

# ========== 訂單相關 API ==========
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
async def create_orders(
    orders_data: CreateOrdersInput,
    authorization: str = Header(None, alias="Authorization")
):
    return OrderController.create_order(orders_data, authorization)

@app.get("/api/order/{orderNumber}")
async def get_orders(
    orderNumber: str,
    authorization: str = Header(None, alias="Authorization")
):
    return OrderController.get_order(orderNumber, authorization)

# ========== 靜態頁面 ==========
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
