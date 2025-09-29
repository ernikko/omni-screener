const API_URL = "https://omni-screener.onrender.com"; // Замените на свой Render URL
const productsTableBody = document.querySelector("#productsTable tbody");
const createProductBtn = document.getElementById("createProductBtn");

// Загрузка и отображение товаров
async function loadProducts() {
  try {
    const res = await fetch(`${API_URL}/get_products`);
    const products = await res.json();

    productsTableBody.innerHTML = ""; // очищаем таблицу

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
    alert("Не удалось загрузить товары. Проверьте бекэнд.");
  }
}

// Создание нового товара
createProductBtn.addEventListener("click", async () => {
  const name = prompt("Введите название товара:");
  const price = parseFloat(prompt("Введите стартовую цену товара:"));

  if (!name || isNaN(price)) return alert("Некорректные данные");

  try {
    const response = await fetch(`${API_URL}/add_product`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, price })
    });

    const product = await response.json();
    if (product && product.id) {
      alert(`Товар "${product.name}" создан!`);
      loadProducts(); // обновляем таблицу
    } else {
      alert("Не удалось создать товар");
    }
  } catch (err) {
    console.error("Ошибка при создании товара:", err);
    alert("Ошибка при создании товара. Проверьте бекэнд.");
  }
});

// Загрузка товаров при старте страницы
loadProducts();
