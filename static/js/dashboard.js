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

  // Mobile compact mode: scale the dashboard to fit 100vh with no scroll
  const fitContainer = document.getElementById("js-fit");
  function fitToViewport() {
    if (!fitContainer) return;
    const isCompact = window.innerWidth <= 640;
    document.body.classList.toggle("mobile-compact", isCompact);
    // Reset before measuring
    fitContainer.style.transform = "";
    fitContainer.style.width = "";
    if (!isCompact) return;
    // Compute scale to fit vertically
    const totalH = fitContainer.scrollHeight;
    const vh = window.innerHeight;
    const scale = Math.min(1, vh / Math.max(1, totalH));
    fitContainer.style.transformOrigin = "top left";
    fitContainer.style.transform = `scale(${scale})`;
    // Expand width so scaled content fills viewport width
    fitContainer.style.width = `${100 / scale}%`;
  }
  window.addEventListener("resize", fitToViewport);
  fitToViewport();

  // Agenda interactions: clicking an item populates the Details panel
  const agenda = document.querySelector(".agenda");
  const detail = document.getElementById("js-detail");
  const dTitle = document.getElementById("js-detail-title");
  const dSummary = document.getElementById("js-detail-summary");
  const dWhen = document.getElementById("js-detail-when");
  const dWhere = document.getElementById("js-detail-where");
  const dSource = document.getElementById("js-detail-source");
  const dLink = document.getElementById("js-detail-link");

  function setDetailsFromEl(el) {
    if (!el || !detail) return;
    const title = el.dataset.title || "Selected item";
    const summary = el.dataset.summary || "";
    const time = el.dataset.time || "";
    const date = el.dataset.date || "";
    const source = el.dataset.source || "";
    const location = el.dataset.location || "";
    const link = el.dataset.link || "";
    if (dTitle) dTitle.textContent = title;
    if (dSummary) dSummary.textContent = summary;
    if (dWhen) dWhen.textContent = [date, time].filter(Boolean).join(" · ") || "—";
    if (dWhere) dWhere.textContent = location || "—";
    if (dSource) dSource.textContent = source || "—";
    if (dLink) {
      if (link) {
        dLink.style.display = "";
        dLink.href = link;
      } else {
        dLink.style.display = "none";
      }
    }
  }

  if (agenda) {
    agenda.addEventListener("click", (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      // If a link inside, try to populate details and keep link default if cmd/ctrl
      const item = target.closest(".agenda-v__item");
      if (item) {
        // Populate and prevent navigation unless modifier used
        const isModified = e.metaKey || e.ctrlKey || e.shiftKey || e.altKey;
        setDetailsFromEl(item);
        if (!isModified) {
          e.preventDefault();
        }
      }
    });
  }
});


