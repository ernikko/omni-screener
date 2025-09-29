const createProductBtn = document.getElementById("createProductBtn");
const productsTableBody = document.querySelector("#productsTable tbody");

// Замените на публичный URL вашего бекэнда Render
const API_URL = "https://omni-screener.onrender.com";

// Функция для обновления таблицы товаров
async function loadProducts() {
  try {
    const res = await fetch(`${API_URL}/get_products`);
    const products = await res.json();

    // Очищаем таблицу
    productsTableBody.innerHTML = "";

    // Добавляем строки
    products.forEach(product => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${product.id}</td>
        <td>${product.name}</td>
        <td>${product.price}</td>
        <td>
          <button class="delete-btn" data-id="${product.id}">Удалить</button>
        </td>
      `;
      productsTableBody.appendChild(row);
    });

    // Привязываем кнопки удаления
    document.querySelectorAll(".delete-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        await fetch(`${API_URL}/delete_product/${id}`, { method: "DELETE" });
        loadProducts();
      });
    });

  } catch (err) {
    console.error("Ошибка при загрузке товаров:", err);
  }
}

// Создание товара
createProductBtn.addEventListener("click", async () => {
  const name = prompt("Название товара:");
  const price = parseFloat(prompt("Цена товара:"));

  if (!name || isNaN(price)) return alert("Некорректные данные");

  try {
    const response = await fetch(`${API_URL}/add_product`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, price })
    });

    if (!response.ok) throw new Error("Ошибка при создании товара");

    loadProducts(); // обновляем таблицу
  } catch (err) {
    console.error(err);
    alert("Не удалось создать товар");
  }
});

// Загрузка товаров при старте
loadProducts();
