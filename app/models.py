# Pydantic modelleri burada tanımlanır

from pydantic import BaseModel, EmailStr
from typing import List

# Kullanıcı kayıt modeli
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# Login modeli
class LoginModel(BaseModel):
    email: EmailStr
    password: str

# Ürün modeli
class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int

# Sipariş ürün alt modeli
class OrderItem(BaseModel):
    product_id: str
    quantity: int

# Sipariş oluşturma modeli
class OrderCreate(BaseModel):
    products: List[OrderItem]

# Status güncelleme modeli
class UpdateStatus(BaseModel):
    status: str
