import { useState } from "react";

export default function Home() {
  const [name, setName] = useState("");
  const [startPrice, setStartPrice] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [product, setProduct] = useState<any>(null);

  const addProduct = async () => {
    const res = await fetch("http://127.0.0.1:8000/add_product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        start_price: parseFloat(startPrice),
        min_price: parseFloat(minPrice),
      }),
    });
    const data = await res.json();
    setProduct(Object.values(data.products).pop());
  };

  return (
    <div className="flex flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-4">Биржа динамических цен</h1>

      <div className="mb-4 flex flex-col gap-2 w-80">
        <input
          type="text"
          placeholder="Название товара"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border p-2 rounded"
        />
        <input
          type="number"
          placeholder="Стартовая цена"
          value={startPrice}
          onChange={(e) => setStartPrice(e.target.value)}
          className="border p-2 rounded"
        />
        <input
          type="number"
          placeholder="Минимальная цена"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
          className="border p-2 rounded"
        />
        <button
          onClick={addProduct}
          className="bg-blue-600 text-white p-2 rounded"
        >
          Добавить товар
        </button>
      </div>

      {product && (
        <div className="border p-4 rounded shadow-md mt-4 w-80">
          <h2 className="text-xl font-semibold">{product.name}</h2>
          <p>Стартовая цена: {product.start_price}</p>
          <p>Минимальная цена: {product.min_price}</p>
          <p>Текущая цена: {product.current_price}</p>
          <p>Просмотров: {product.views}</p>
        </div>
      )}
    </div>
  );
}
