from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Временная база в памяти (для MVP, потом заменим на Supabase/Postgres)
products: Dict[int, dict] = {}
product_id_counter = 1

class Product(BaseModel):
    name: str
    start_price: float
    min_price: float

class UpdateDemand(BaseModel):
    product_id: int
    views: int  # условно: сколько раз карточку посмотрели

@app.post("/add_product")
def add_product(product: Product):
    global product_id_counter
    products[product_id_counter] = {
        "id": product_id_counter,
        "name": product.name,
        "start_price": product.start_price,
        "min_price": product.min_price,
        "current_price": product.start_price,
        "views": 0
    }
    product_id_counter += 1
    return {"status": "ok", "products": products}

@app.post("/update_price")
def update_price(data: UpdateDemand):
    product = products.get(data.product_id)
    if not product:
        return {"error": "Product not found"}
    product["views"] += data.views
    # простая логика: чем больше просмотров, тем выше цена
    product["current_price"] = max(
        product["min_price"], 
        product["start_price"] * (1 + product["views"] * 0.05)  # +5% за каждые 10 просмотров
    )
    return {"status": "updated", "product": product}

@app.get("/get_product/{product_id}")
def get_product(product_id: int):
    product = products.get(product_id)
    if not product:
        return {"error": "Product not found"}
    return product
