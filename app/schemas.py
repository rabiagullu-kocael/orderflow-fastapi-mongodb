"""
API request ve response modelleri (Pydantic)
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List
from datetime import datetime


# =========================
# USER SCHEMAS
# =========================

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr


# =========================
# PRODUCT SCHEMAS
# =========================

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)


class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    stock: int


# =========================
# ORDER SCHEMAS
# =========================

class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    products: List[OrderItem]


class OrderResponse(BaseModel):
    id: str
    user_id: str
    products: List[OrderItem]
    total_price: float
    status: str
    createdAt: datetime


class OrderStatusUpdate(BaseModel):
    status: str


