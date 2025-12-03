async function loadChangeNewHaven() {
  try {
    const res = await fetch("/api/change-new-haven-live", { headers: { "Accept": "application/json" } });
    if (!res.ok) throw new Error("Failed");
    const items = await res.json();
    const grid = document.getElementById("cnn-live-grid");
    if (!grid) return;
    grid.innerHTML = "";
    (items || []).forEach((item) => {
      const card = document.createElement("a");
      card.className = "cnn-live-card";
      card.href = item.url || "#";
      card.target = "_blank";
      card.rel = "noopener";
      card.innerHTML = `
        <div class="cnn-live-title">${(item.title || "").slice(0, 120)}</div>
        <div class="cnn-live-category">${item.category || ""}</div>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    const grid = document.getElementById("cnn-live-grid");
    if (grid) grid.innerHTML = "<div class='cnn-live-error'>Failed to load.</div>";
  }
}
loadChangeNewHaven();
setInterval(loadChangeNewHaven, 1800000);


