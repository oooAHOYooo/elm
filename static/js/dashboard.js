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
  // Disabled when mobile nav is active (mobile-nav.js handles mobile layout)
  const fitContainer = document.getElementById("js-fit");
  function fitToViewport() {
    if (!fitContainer) return;
    // Check if mobile nav is active
    const isMobileNavActive = window.mobileNav && window.mobileNav.isMobile();
    if (isMobileNavActive) {
      // Mobile nav handles layout, don't scale
      fitContainer.style.transform = "";
      fitContainer.style.width = "";
      return;
    }
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
  // Delay to let mobile-nav initialize first
  setTimeout(fitToViewport, 100);
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

  // Tiny tides widget (no scrolling, micro text)
  const tideDate = document.getElementById("js-tide-date");
  const tideOutput = document.getElementById("js-tide-output");

  async function fetchTides() {
    if (!tideDate || !tideOutput) return;
    const station = "8465705"; // New Haven fixed
    const day = tideDate.value || "today";
    try {
      tideOutput.textContent = "Tides loading…";
      const resp = await fetch(`/api/tides?station=${encodeURIComponent(station)}&date=${encodeURIComponent(day)}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      const preds = Array.isArray(data.predictions) ? data.predictions : [];
      if (preds.length === 0) {
        tideOutput.textContent = "No tides.";
        return;
      }
      // Render minimal lines: e.g., High 7:12 AM · 5.1 ft
      const lines = preds.slice(0, 4).map(p => {
        const t = p.t || "";
        const type = p.type === "H" ? "High" : "Low";
        const h = Number(p.v);
        // Format time as h:mm AM/PM
        const dt = new Date(t.replace(" ", "T"));
        const timeStr = dt.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
        const height = isFinite(h) ? `${h.toFixed(1)} ft` : "";
        return `${type} ${timeStr} · ${height}`;
      });
      tideOutput.textContent = lines.join("  ·  ");
    } catch (err) {
      tideOutput.textContent = "Tides unavailable.";
    }
  }
  if (tideDate) {
    tideDate.addEventListener("change", fetchTides);
    fetchTides();
  }

  // Temperature units switcher (F/C) for current, H/L, and dayparts
  const unitsSelect = document.getElementById("js-units");
  function toC(f) {
    return (f - 32) * 5 / 9;
  }
  function fmt(n) {
    // Round to nearest integer
    return Math.round(n);
  }
  function applyUnits() {
    if (!unitsSelect) return;
    const units = unitsSelect.value || "F";
    // Current temp(s)
    document.querySelectorAll("[data-temp-f]").forEach(el => {
      const fStr = el.getAttribute("data-temp-f");
      const fVal = fStr ? Number(fStr) : NaN;
      if (!isFinite(fVal)) return;
      const val = units === "F" ? fVal : toC(fVal);
      el.textContent = `${fmt(val)}°`;
    });
    // High / Low
    const hilo = document.getElementById("js-hilo");
    if (hilo) {
      const hiStr = hilo.getAttribute("data-high-f");
      const loStr = hilo.getAttribute("data-low-f");
      const hiF = hiStr ? Number(hiStr) : NaN;
      const loF = loStr ? Number(loStr) : NaN;
      const hi = isFinite(hiF) ? (units === "F" ? hiF : toC(hiF)) : null;
      const lo = isFinite(loF) ? (units === "F" ? loF : toC(loF)) : null;
      const hiTxt = hi == null ? "—" : `${fmt(hi)}°`;
      const loTxt = lo == null ? "—" : `${fmt(lo)}°`;
      hilo.textContent = `H ${hiTxt} · L ${loTxt}`;
    }
    // Persist preference
    try { localStorage.setItem("units", units); } catch {}
  }
  if (unitsSelect) {
    try {
      const saved = localStorage.getItem("units");
      if (saved && (saved === "F" || saved === "C")) {
        unitsSelect.value = saved;
      }
    } catch {}
    unitsSelect.addEventListener("change", applyUnits);
    applyUnits();
  }
});


