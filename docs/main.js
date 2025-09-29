const API_URL = "https://omni-screener.onrender.com"; // <- замени на публичный адрес, например https://my-service.onrender.com

const tbody = document.querySelector("#productsTable tbody");
const createBtn = document.getElementById("createProductBtn");

async function loadProducts(){
  try{
    const r = await fetch(`${API_URL}/get_products`);
    const products = await r.json();
    tbody.innerHTML = "";
    products.forEach(p=>{
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.id}</td>
        <td class="name-cell" data-id="${p.id}">${escapeHtml(p.name)}</td>
        <td>${p.start_price.toFixed(2)}</td>
        <td class="${p.current_price >= p.start_price ? 'price-up' : 'price-down'}">${p.current_price.toFixed(2)}</td>
        <td>${p.demand_counter}</td>
        <td>
          <button class="btn btn-sm btn-danger delete-btn" data-id="${p.id}">Удалить</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // delete handlers
    document.querySelectorAll(".delete-btn").forEach(btn=>{
      btn.onclick = async (e)=>{
        const id = btn.dataset.id;
        await fetch(`${API_URL}/delete_product/${id}`, { method: "DELETE" });
        await loadProducts();
      };
    });

    // click on name => simulate add to cart (demand)
    document.querySelectorAll(".name-cell").forEach(cell=>{
      cell.onclick = async (e)=>{
        const id = cell.dataset.id;
        await fetch(`${API_URL}/update_demand/${id}`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({delta:1}) });
        await loadProducts();
      };
      cell.style.cursor = "pointer";
      cell.title = "Нажмите, чтобы добавить в корзину (увеличить спрос)";
    });

  }catch(err){
    console.error("loadProducts error", err);
  }
}

createBtn.onclick = async ()=>{
  const name = prompt("Название товара:");
  const price = parseFloat(prompt("Стартовая / минимальная цена:"));
  if(!name || isNaN(price)) return alert("Некорректные данные");
  try{
    const r = await fetch(`${API_URL}/add_product`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({name, price})});
    const data = await r.json();
    if(data && data.success) await loadProducts();
    else alert("Не удалось создать товар");
  }catch(e){
    console.error("create error", e);
    alert("Ошибка при создании товара");
  }
};

function escapeHtml(str){
  return str.replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
}

loadProducts();

