f# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Разрешаем запросы с любого фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Структура товара
class Product(BaseModel):
    name: str
    price: float

# Хранилище товаров (пока в памяти)
products = []
product_id = 1

@app.post("/add_product")
async def add_product(product: Product):
    global product_id
    new_product = {"id": product_id, "name": product.name, "price": product.price}
    products.append(new_product)
    product_id += 1
    return new_product

@app.get("/get_products")
async def get_products():
    return products
