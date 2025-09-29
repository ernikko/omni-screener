const backendUrl = "https://omni-screener-production.up.railway.app";

const createBtn = document.getElementById("createProductBtn");
const tableBody = document.querySelector("#productsTable tbody");

// Локальная копия товаров (для отображения)
let products = {};

// Функция рендера таблицы
function renderTable() {
  tableBody.innerHTML = "";
  for (const [id, product] of Object.entries(products)) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${id}</td>
      <td>${product.name}</td>
      <td>${product.current_price}</td>
      <td>
        <button onclick="addView(${id})">Добавить просмотр</button>
      </td>
    `;
    tableBody.appendChild(tr);
  }
}

// Создание нового товара
createBtn.addEventListener("click", async () => {
  const name = prompt("Введите название товара:");
  if (!name) return;

  const startPrice = parseFloat(prompt("Введите стартовую цену:", "100"));
  const minPrice = parseFloat(prompt("Введите минимальную цену:", "50"));
  if (isNaN(startPrice) || isNaN(minPrice)) return alert("Неверная цена!");

  const res = await fetch(`${backendUrl}/add_product`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, start_price: startPrice, min_price: minPrice })
  });
  const data = await res.json();
  products = data.products;
  renderTable();
});

// Добавление просмотра (увеличение цены)
async function addView(id) {
  const res = await fetch(`${backendUrl}/update_price`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ product_id: id, views: 1 })
  });
  const data = await res.json();
  products[id] = data.product;
  renderTable();
}

// Начальная загрузка товаров с бекэнда
async function loadProducts() {
  try {
    const res = await fetch(`${backendUrl}/get_products`);
    const data = await res.json();
    products = data.products || {};
    renderTable();
  } catch (err) {
    console.error("Ошибка загрузки товаров", err);
  }
}

loadProducts();

