document.addEventListener("DOMContentLoaded", () => {
  const checkboxes = Array.from(document.querySelectorAll(".js-filter"));
  const cards = Array.from(document.querySelectorAll(".card"));
  const mapSelect = document.getElementById("js-map-select");
  const mapFrame = document.getElementById("js-map-frame");

  function applyFilters() {
    const allowed = new Set(
      checkboxes.filter(cb => cb.checked).map(cb => cb.getAttribute("data-category"))
    );
    cards.forEach(card => {
      const cat = card.getAttribute("data-category") || "news";
      card.style.display = allowed.has(cat) ? "" : "none";
    });
  }

  checkboxes.forEach(cb => cb.addEventListener("change", applyFilters));
  applyFilters();

  // Maps: build OSM embed URL for selected layer
  function updateMap() {
    if (!mapSelect || !mapFrame) return;
    const layer = mapSelect.value || "mapnik";
    const center = (window.MAP_CENTER) ||
      (mapFrame && mapFrame.dataset && {
        lat: parseFloat(mapFrame.dataset.lat || "41.3101"),
        lon: parseFloat(mapFrame.dataset.lon || "-72.9241"),
      }) ||
      { lat: 41.3101, lon: -72.9241 };
    const lat = Number(center.lat || 41.3101);
    const lon = Number(center.lon || -72.9241);
    // Simple bbox around center (about ~10-12km span)
    const dLat = 0.06;
    const dLon = 0.08;
    const minLat = (lat - dLat).toFixed(5);
    const maxLat = (lat + dLat).toFixed(5);
    const minLon = (lon - dLon).toFixed(5);
    const maxLon = (lon + dLon).toFixed(5);
    const src = `https://www.openstreetmap.org/export/embed.html?bbox=${minLon},${minLat},${maxLon},${maxLat}&layer=${encodeURIComponent(layer)}&marker=${lat},${lon}`;
    mapFrame.src = src;
  }
  if (mapSelect) {
    mapSelect.addEventListener("change", updateMap);
  }
  // initialize map once
  updateMap();
});


