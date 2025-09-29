const backendUrl = "omni-screener-production.up.railway.app"; // сюда вставь свой URL Railway

const createBtn = document.getElementById("createProductBtn");
const tableBody = document.querySelector("#productsTable tbody");

let products = {};

// Рендер таблицы с подсветкой динамики
function renderTable() {
  tableBody.innerHTML = "";
  for (const [id, p] of Object.entries(products)) {
    const priceClass = p.current_price >= p.start_price ? "price-up" : "price-down";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.name}</td>
      <td>${p.start_price.toFixed(2)}</td>
      <td class="${priceClass}">${p.current_price.toFixed(2)}</td>
      <td>${p.current_price - p.start_price >= 0 ? '+' : ''}${(p.current_price - p.start_price).toFixed(2)}</td>
      <td>
        <button class="btn btn-sm btn-primary" onclick="addView('${id}')">+Просмотр</button>
      </td>
    `;
    tableBody.appendChild(tr);
  }
}

// Создание нового товара
createBtn.addEventListener("click", async () => {
  const name = prompt("Название товара:");
  const price = parseFloat(prompt("Стартовая/минимальная цена:"));
  if (!name || isNaN(price)) return alert("Неверные данные!");

  try {
    const res = await fetch(`${backendUrl}/add_product`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, start_price: price, min_price: price })
    });
    const data = await res.json();
    if (data.success) {
      products = data.products;
      renderTable();
    } else {
      alert("Не удалось создать товар.");
    }
  } catch (err) {
    console.error(err);
    alert("Не удалось создать товар. Проверь бекэнд.");
  }
});

// Добавление «просмотра» (увеличение цены)
async function addView(id) {
  try {
    const res = await fetch(`${backendUrl}/update_price`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: id, views: 1 })
    });
    const data = await res.json();
    if (data.success) {
      products[id] = data.product;
      renderTable();
    } else {
      alert("Не удалось обновить цену.");
    }
  } catch (err) {
    console.error(err);
    alert("Не удалось обновить цену.");
  }
}

// Загрузка товаров при старте
async function loadProducts() {
  try {
    const res = await fetch(`${backendUrl}/get_products`);
    const data = await res.json();
    products = data.products || {};
    renderTable();
  } catch (err) {
    console.error(err);
    alert("Не удалось загрузить товары.");
  }
}

// Обновляем таблицу каждые 10 секунд для динамики
setInterval(loadProducts, 10000);

loadProducts();
