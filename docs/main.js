const backendUrl = "https://omni-screener-production.up.railway.app";

const testBtn = document.getElementById("testBtn");
const updateBtn = document.getElementById("updateBtn");
const productInfo = document.getElementById("productInfo");

// Кнопка "Создать товар"
testBtn.addEventListener("click", async () => {
  try {
    const res = await fetch(`${backendUrl}/add_product`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Тестовый товар",
        start_price: 100,
        min_price: 50
      }),
    });
    const data = await res.json();
    const product = Object.values(data.products).pop();
    productInfo.innerText = `Название: ${product.name}\nТекущая цена: ${product.current_price}`;
  } catch (err) {
    console.error(err);
    productInfo.innerText = "Ошибка при создании товара.";
  }
});

// Кнопка "Добавить просмотр" (увеличивает цену)
updateBtn.addEventListener("click", async () => {
  try {
    const productId = 1; // для MVP берём первый товар
    const res = await fetch(`${backendUrl}/update_price`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, views: 1 }),
    });
    const data = await res.json();
    productInfo.innerText = `Название: ${data.product.name}\nТекущая цена: ${data.product.current_price}`;
  } catch (err) {
    console.error(err);
    productInfo.innerText = "Ошибка при обновлении цены.";
  }
});
