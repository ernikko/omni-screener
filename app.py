# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List
import os

DB_PATH = os.getenv("DATABASE_PATH", "data.db")

app = FastAPI(title="TQTVL System API")

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на MVP: разрешаем всё; в проде — конкретные домены
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic модели
class ProductIn(BaseModel):
    name: str
    price: float  # стартовая / минимальная цена

class WebhookEvent(BaseModel):
    platform: str
    event: str
    product_external_id: str
    quantity: int = 1

# --- DB helpers ---
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        start_price REAL NOT NULL,
        min_price REAL NOT NULL,
        current_price REAL NOT NULL,
        demand_counter INTEGER NOT NULL DEFAULT 0,
        external_id TEXT
    )
    """)
    conn.commit()
    conn.close()

# инициализация БД при старте
init_db()

# --- Логика пересчёта цены ---
def recalc_price(start_price: float, min_price: float, demand_counter: int) -> float:
    # Простая формула: +2% от start_price за каждую единицу спроса
    # (можно усложнить: логарифм, экспонента и т.д.)
    new_price = start_price * (1 + 0.02 * demand_counter)
    if new_price < min_price:
        return min_price
    return round(new_price, 2)

# --- Эндпоинты ---
@app.get("/get_products")
def get_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "name": r["name"],
            "start_price": r["start_price"],
            "min_price": r["min_price"],
            "current_price": r["current_price"],
            "demand_counter": r["demand_counter"],
            "external_id": r["external_id"],
        })
    return result

@app.post("/add_product")
def add_product(item: ProductIn):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, start_price, min_price, current_price, demand_counter) VALUES (?, ?, ?, ?, ?)",
        (item.name, item.price, item.price, item.price, 0)
    )
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    return {"success": True, "product": {"id": product_id, "name": item.name, "start_price": item.price, "min_price": item.price, "current_price": item.price, "demand_counter": 0}}

@app.delete("/delete_product/{id}")
def delete_product(id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (id,))
    changed = cur.rowcount
    conn.commit()
    conn.close()
    if changed:
        return {"success": True}
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/update_demand/{id}")
def update_demand(id: int, payload: dict = None):
    """
    Увеличить спрос на товар — вызывается когда покупатель добавил товар в корзину
    payload можно использовать для количества: {"delta": 1}
    """
    delta = 1
    if payload and isinstance(payload, dict):
        try:
            delta = int(payload.get("delta", 1))
        except:
            delta = 1

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT start_price, min_price, demand_counter FROM products WHERE id = ?", (id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    start_price = row["start_price"]
    min_price = row["min_price"]
    demand = row["demand_counter"] + delta
    new_price = recalc_price(start_price, min_price, demand)
    cur.execute("UPDATE products SET demand_counter = ?, current_price = ? WHERE id = ?", (demand, new_price, id))
    conn.commit()
    conn.close()
    return {"success": True, "product": {"id": id, "current_price": new_price, "demand_counter": demand}}

@app.post("/webhook")
async def webhook(event: WebhookEvent):
    """
    Приход с внешней платформы (пример заглушки).
    Можно: найти product по external_id и применить изменение спроса.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, demand_counter FROM products WHERE external_id = ?", (event.product_external_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"success": False, "reason": "product not found"}
    product_id = row["id"]
    # если event.event == "add_to_cart" -> увеличиваем demand
    if event.event == "add_to_cart":
        cur.execute("UPDATE products SET demand_counter = demand_counter + ? WHERE id = ?", (event.quantity, product_id))
        conn.commit()
        # пересчитать цену
        cur.execute("SELECT start_price, min_price, demand_counter FROM products WHERE id = ?", (product_id,))
        r = cur.fetchone()
        new_price = recalc_price(r["start_price"], r["min_price"], r["demand_counter"])
        cur.execute("UPDATE products SET current_price = ? WHERE id = ?", (new_price, product_id))
        conn.commit()
    conn.close()
    return {"success": True}
