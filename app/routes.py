# Tüm endpointler burada tanımlanır

from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from datetime import datetime
from typing import Optional, List
from app.database import db
from app.models import *
from app.auth import hash_password, verify_password, create_access_token
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# JWT security sistemi
security = HTTPBearer()

# -------------------------------------------------
# JWT'den current user'ı almak için helper fonksiyon
# -------------------------------------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# -------------------------------------------------
# USER REGISTER
# -------------------------------------------------
@router.post("/register")
def register(user: UserCreate):

    # Email kontrolü
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Şifre hashlenir
    hashed_pw = hash_password(user.password)

    user_data = {
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_pw
    }

    result = db.users.insert_one(user_data)

    return {
        "message": "User created",
        "user_id": str(result.inserted_id)
    }


# -------------------------------------------------
# LOGIN
# -------------------------------------------------
@router.post("/login")
def login(user: LoginModel):

    db_user = db.users.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Token oluşturulur (sub içine user_id koyuyoruz)
    token = create_access_token({"sub": str(db_user["_id"])})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------------------------------
# PRODUCT CREATE
# -------------------------------------------------
@router.post("/products")
def create_product(product: ProductCreate):

    result = db.products.insert_one(product.dict())

    return {
        "message": "Product created",
        "product_id": str(result.inserted_id)
    }


# -------------------------------------------------
# ORDER CREATE
# -------------------------------------------------
@router.post("/orders")
def create_order(order: OrderCreate, user_id: str = Depends(get_current_user)):

    total_price = 0
    order_products = []

    for item in order.products:

        product = db.products.find_one({"_id": ObjectId(item.product_id)})

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        # Toplam hesaplanır
        total_price += product["price"] * item.quantity

        # Stok düşülür
        db.products.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}}
        )

        order_products.append({
            "product_id": item.product_id,
            "quantity": item.quantity
        })

    order_data = {
        "user_id": user_id,  # JWT’den gelen user_id
        "products": order_products,
        "total_price": total_price,
        "status": "pending",
        "createdAt": datetime.utcnow()
    }

    result = db.orders.insert_one(order_data)

    return {
        "message": "Order created",
        "order_id": str(result.inserted_id)
    }


# -------------------------------------------------
# ORDER LIST (Filter + Sort destekli)
# -------------------------------------------------
@router.get("/orders")
def list_orders(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = None
):

    query = {}

    # user filtre
    if user_id:
        query["user_id"] = user_id

    # status filtre
    if status:
        if status not in ["pending", "shipped", "delivered"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        query["status"] = status

    cursor = db.orders.find(query)

    # sorting
    if sort_by == "price_desc":
        cursor = cursor.sort("total_price", -1)
    elif sort_by == "price_asc":
        cursor = cursor.sort("total_price", 1)
    elif sort_by == "date_desc":
        cursor = cursor.sort("createdAt", -1)

    orders = []

    for order in cursor:
        order["_id"] = str(order["_id"])
        orders.append(order)

    return orders


# -------------------------------------------------
# ORDER STATUS UPDATE
# -------------------------------------------------
@router.patch("/orders/{order_id}/status")
def update_status(order_id: str, status_update: UpdateStatus):

    if status_update.status not in ["pending", "shipped", "delivered"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    result = db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": status_update.status}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order status updated"}


# -------------------------------------------------
# ORDER STATS (Günlük sipariş sayısı + ciro)
# -------------------------------------------------
@router.get("/orders/stats")
def order_stats():

    pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$createdAt"},
                    "month": {"$month": "$createdAt"},
                    "day": {"$dayOfMonth": "$createdAt"}
                },
                "total_orders": {"$sum": 1},
                "total_revenue": {"$sum": "$total_price"}
            }
        }
    ]

    stats = list(db.orders.aggregate(pipeline))

    for stat in stats:
        stat["_id"] = f"{stat['_id']['year']}-{stat['_id']['month']}-{stat['_id']['day']}"

    return stats
