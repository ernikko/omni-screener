from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import uuid

app = FastAPI()

# Разрешаем доступ с любого фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# В памяти храним товары
products: Dict[str, dict] = {}

# Модель для добавления товара
class ProductInput(BaseModel):
    name: str
    start_price: float
    min_price: float

# Модель для обновления цены
class UpdateInput(BaseModel):
    product_id: str
    views: int = 0

# Получить все товары
@app.get("/get_products")
def get_products():
    return {"products": products}

# Добавить товар
@app.post("/add_product")
def add_product(item: ProductInput):
    product_id = str(uuid.uuid4())
    products[product_id] = {
        "id": product_id,
        "name": item.name,
        "start_price": item.start_price,
        "min_price": item.min_price,
        "current_price": item.start_price,
        "last_change": 0
    }
    return {"success": True, "products": products}

# Обновить цену товара
@app.post("/update_price")
def update_price(update: UpdateInput):
    if update.product_id not in products:
        return {"error": "Товар не найден"}
    product = products[update.product_id]
    # Простая динамика: цена растет на 1% за каждый просмотр
    change = product["current_price"] * 0.01 * update.views
    product["current_price"] += change
    product["last_change"] = change
    products[update.product_id] = product
    return {"success": True, "product": product}
