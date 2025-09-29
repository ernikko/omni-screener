from fastapi import FastAPI, HTTPException
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

# Модель товара
class Product(BaseModel):
    name: str
    price: float

# Хранилище товаров в памяти
products = []
product_id_counter = 1

@app.post("/add_product")
async def add_product(product: Product):
    global product_id_counter
    new_product = {
        "id": product_id_counter,
        "name": product.name,
        "price": product.price
    }
    products.append(new_product)
    product_id_counter += 1
    return new_product  # возвращаем объект с id, name, price

@app.get("/get_products")
async def get_products():
    return products

@app.delete("/delete_product/{id}")
async def delete_product(id: int):
    global products
    for p in products:
        if p["id"] == id:
            products = [x for x in products if x["id"] != id]
            return {"success": True}  # фронт проверяет success
    raise HTTPException(status_code=404, detail="Product not found")
