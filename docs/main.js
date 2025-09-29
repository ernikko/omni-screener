const API_URL = "https://omni-screener.onrender.com"; // замените на ваш Render URL

const productsTableBody = document.querySelector("#productsTable tbody");
const createProductBtn = document.getElementById("createProductBtn");

// Функция загрузки товаров
async function loadProducts() {
  try {
    const res = await fetch(`${API_URL}/get_products`);
    const products = await res.json();

    productsTableBody.innerHTML = "";

    products.forEach(product => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${product.id}</td>
        <td class="clickable" data-id="${product.id}">${product.name}</td>
        <td>${product.start_price.toFixed(2)}</td>
        <td>${product.current_price.toFixed(2)}</td>
        <td>${product.demand_counter}</td>
        <td>
          <button class="btn btn-sm btn-danger delete-btn" data-id="${product.id}">Удалить</button>
        </td>
      `;
      productsTableBody.appendChild(row);
    });

    // Кнопки удаления
    document.querySelectorAll(".delete-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        await fetch(`${API_URL}/delete_product/${id}`, { method: "DELETE" });
        loadProducts();
      });
    });

    // Клик по товару для увеличения спроса
    document.querySelectorAll(".clickable").forEach(cell => {
      cell.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        const res = await fetch(`${API_URL}/update_demand/${id}`, { method: "POST" });
        if (res.ok) loadProducts();
      });
    });

  } catch (err) {
    console.error("Ошибка при загрузке товаров:", err);
  }
}

// Добавление нового товара
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

    const data = await response.json();
    if (data.success) loadProducts();
    else alert("Не удалось создать товар");

  } catch (err) {
    console.error(err);
    alert("Ошибка при создании товара");
  }
});

// Загрузка товаров при старте
loadProducts();

