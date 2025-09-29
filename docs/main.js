const productsTable = document.getElementById("productsTable").getElementsByTagName('tbody')[0];
const createProductBtn = document.getElementById("createProductBtn");

createProductBtn.addEventListener("click", async () => {
  try {
    const name = prompt("Введите название товара:");
    const price = parseFloat(prompt("Введите стартовую цену товара:"));
    if (!name || isNaN(price)) return alert("Некорректные данные");

    // API-запрос к бекэнду Railway
    const response = await fetch("https://omni-screener.onrender.com/add_product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, price })
    });

    const data = await response.json();
    if (data.success) {
      addProductRow(data.product);
    } else {
      alert("Не удалось создать товар");
    }
  } catch (e) {
    console.error(e);
    alert("Ошибка при создании товара");
  }
});

function addProductRow(product) {
  const row = productsTable.insertRow();
  row.innerHTML = `
    <td>${product.name}</td>
    <td>${product.start_price}</td>
    <td>${product.current_price}</td>
    <td class="${product.delta >=0 ? 'price-up' : 'price-down'}">${product.delta}</td>
    <td><button class="btn btn-sm btn-danger" onclick="deleteProduct('${product.id}', this)">Удалить</button></td>
  `;
}

async function deleteProduct(id, btn) {
  try {
    const res = await fetch(`https://omni-screener-production.up.railway.app/delete_product/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      btn.closest("tr").remove();
    } else {
      alert("Не удалось удалить товар");
    }
  } catch (e) {
    console.error(e);
    alert("Ошибка при удалении товара");
  }
}
