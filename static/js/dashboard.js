document.addEventListener("DOMContentLoaded", () => {
  // --- Dark Mode Toggle ---
  const darkToggle = document.getElementById("js-dark-toggle");
  const root = document.documentElement;
  
  function getPreferredTheme() {
    const stored = localStorage.getItem("theme");
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  
  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    // Update toggle icon
    const icon = darkToggle ? darkToggle.querySelector(".dark-mode-icon") : null;
    if (icon) {
      icon.textContent = theme === "dark" ? "☀️" : "🌙";
      icon.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
    }
  }
  
  // Initialize theme
  setTheme(getPreferredTheme());
  
  if (darkToggle) {
    darkToggle.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") || "light";
      setTheme(current === "dark" ? "light" : "dark");
    });
  }
  
  // Listen for system preference changes
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (!localStorage.getItem("theme")) {
      setTheme(e.matches ? "dark" : "light");
    }
  });

  const checkboxes = Array.from(document.querySelectorAll(".js-filter"));
  const cards = Array.from(document.querySelectorAll(".card"));
  const mapSelect = document.getElementById("js-map-select");
  const mapFrame = document.getElementById("js-map-frame");

  // --- Enhanced Category Filtering ---
  function applyFilters() {
    const allowed = new Set(
      checkboxes.filter(cb => cb.checked).map(cb => cb.getAttribute("data-category"))
    );
    cards.forEach(card => {
      const cat = card.getAttribute("data-category") || "news";
      card.style.display = allowed.has(cat) ? "" : "none";
    });
    
    // Save filter preferences
    try {
      const prefs = {};
      checkboxes.forEach(cb => {
        prefs[cb.getAttribute("data-category")] = cb.checked;
      });
      localStorage.setItem("filterPrefs", JSON.stringify(prefs));
    } catch (e) {}
  }

  // Load saved filter preferences
  try {
    const savedPrefs = JSON.parse(localStorage.getItem("filterPrefs") || "{}");
    if (Object.keys(savedPrefs).length > 0) {
      checkboxes.forEach(cb => {
        const cat = cb.getAttribute("data-category");
        if (cat in savedPrefs) {
          cb.checked = savedPrefs[cat];
        }
      });
    }
  } catch (e) {}

  checkboxes.forEach(cb => cb.addEventListener("change", applyFilters));
  applyFilters();

  // Select All / Clear All buttons
  const filterAllBtn = document.getElementById("js-filter-all");
  const filterNoneBtn = document.getElementById("js-filter-none");
  
  if (filterAllBtn) {
    filterAllBtn.addEventListener("click", () => {
      checkboxes.forEach(cb => cb.checked = true);
      applyFilters();
    });
  }
  
  if (filterNoneBtn) {
    filterNoneBtn.addEventListener("click", () => {
      checkboxes.forEach(cb => cb.checked = false);
      applyFilters();
    });
  }

  // --- Neighborhood Filter ---
  const neighborhoodSelect = document.getElementById("js-neighborhood");
  
  if (neighborhoodSelect) {
    // Load saved neighborhood
    try {
      const savedNeighborhood = localStorage.getItem("neighborhoodFilter");
      if (savedNeighborhood) {
        neighborhoodSelect.value = savedNeighborhood;
      }
    } catch (e) {}
    
    neighborhoodSelect.addEventListener("change", () => {
      const neighborhood = neighborhoodSelect.value;
      localStorage.setItem("neighborhoodFilter", neighborhood);
      
      // Visual feedback - flash the filter
      neighborhoodSelect.style.borderColor = "var(--accent)";
      setTimeout(() => {
        neighborhoodSelect.style.borderColor = "";
      }, 300);
      
      // In future: filter events/news by neighborhood
      // For now, just store the preference
      console.log("Neighborhood filter set to:", neighborhood);
      
      // Could trigger a re-fetch with neighborhood param
      // fetchWeekEvents(currentWeekOffset, neighborhood);
    });
  }

  // --- Data Freshness Tracking ---
  const pageLoadTime = Date.now();
  
  function updateFreshnessIndicators() {
    const elapsed = Math.floor((Date.now() - pageLoadTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    
    const freshnessElements = document.querySelectorAll(".data-freshness");
    freshnessElements.forEach(el => {
      const dot = el.querySelector(".freshness-dot");
      const text = el.querySelector(".freshness-text");
      
      if (minutes < 5) {
        if (dot) {
          dot.className = "freshness-dot";
        }
        if (text) {
          text.textContent = elapsed < 60 ? "Updated just now" : `Updated ${minutes}m ago`;
        }
      } else if (minutes < 15) {
        if (dot) {
          dot.className = "freshness-dot freshness-dot--stale";
        }
        if (text) {
          text.textContent = `Updated ${minutes}m ago`;
        }
      } else {
        if (dot) {
          dot.className = "freshness-dot freshness-dot--stale";
        }
        if (text) {
          text.textContent = `Updated ${minutes}m ago · Refresh for latest`;
        }
      }
    });
  }
  
  // Update freshness every 30 seconds
  setInterval(updateFreshnessIndicators, 30000);
  updateFreshnessIndicators();

  // --- Refresh Button ---
  const refreshBtn = document.getElementById("js-refresh");
  
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      refreshBtn.classList.add("is-refreshing");
      // Reload the page after a brief animation
      setTimeout(() => {
        window.location.reload();
      }, 500);
    });
  }

  // --- Auto-Refresh Toggle ---
  const autoRefreshToggle = document.getElementById("js-auto-refresh-toggle");
  let autoRefreshInterval = null;
  const AUTO_REFRESH_MS = 5 * 60 * 1000; // 5 minutes
  
  function setAutoRefresh(enabled) {
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
      autoRefreshInterval = null;
    }
    
    if (enabled) {
      autoRefreshInterval = setInterval(() => {
        console.log("Auto-refreshing...");
        window.location.reload();
      }, AUTO_REFRESH_MS);
      
      if (autoRefreshToggle) {
        autoRefreshToggle.textContent = "ON";
        autoRefreshToggle.classList.add("is-active");
      }
    } else {
      if (autoRefreshToggle) {
        autoRefreshToggle.textContent = "OFF";
        autoRefreshToggle.classList.remove("is-active");
      }
    }
    
    // Save preference
    try {
      localStorage.setItem("autoRefresh", enabled ? "on" : "off");
    } catch (e) {}
  }
  
  // Load saved auto-refresh preference
  try {
    const savedAutoRefresh = localStorage.getItem("autoRefresh");
    if (savedAutoRefresh === "on") {
      setAutoRefresh(true);
    }
  } catch (e) {}
  
  if (autoRefreshToggle) {
    autoRefreshToggle.addEventListener("click", () => {
      const isActive = autoRefreshToggle.classList.contains("is-active");
      setAutoRefresh(!isActive);
    });
  }

  // --- Keyboard Shortcuts ---
  document.addEventListener("keydown", (e) => {
    // Ctrl/Cmd + R is already handled by browser
    // Add custom shortcuts
    
    // 'D' for dark mode toggle (when not in input)
    if (e.key === "d" && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const target = e.target;
      if (target.tagName !== "INPUT" && target.tagName !== "TEXTAREA" && target.tagName !== "SELECT") {
        if (darkToggle) {
          darkToggle.click();
        }
      }
    }
    
    // 'R' for refresh (when not in input)
    if (e.key === "r" && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const target = e.target;
      if (target.tagName !== "INPUT" && target.tagName !== "TEXTAREA" && target.tagName !== "SELECT") {
        if (refreshBtn) {
          refreshBtn.click();
        }
      }
    }
    
    // Escape to close mobile details panel
    if (e.key === "Escape") {
      if (detail && detail.classList.contains("is-open")) {
        detail.classList.remove("is-open");
      }
    }
  });

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
    fitContainer.style.transform = ""; // DISABLED: User wants native scrolling on mobile now
    fitContainer.style.width = ""; // Reset
    document.body.classList.remove("mobile-compact");
  }
  // window.addEventListener("resize", fitToViewport);
  // setTimeout(fitToViewport, 100);
  // fitToViewport(); 
  // DISABLED SCALING logic above per request for native scroll on mobile
  
  // Agenda interactions: clicking an item populates the Details panel
  const agenda = document.getElementById("js-agenda-week");
  const detail = document.getElementById("js-detail");
  const dTitle = document.getElementById("js-detail-title");
  const dSummary = document.getElementById("js-detail-summary");
  const dWhen = document.getElementById("js-detail-when");
  const dWhere = document.getElementById("js-detail-where");
  const dSource = document.getElementById("js-detail-source");
  const dLink = document.getElementById("js-detail-link");

  function setDetailsFromEl(el) {
    if (!el || !detail) return;
    
    // Toggle active state
    const allItems = document.querySelectorAll('.week-event-item, .ecd-event-card');
    allItems.forEach(i => i.classList.remove('is-selected'));
    el.classList.add('is-selected');

    const title = el.dataset.title || "Selected item";
    const summary = el.dataset.summary || "";
    const time = el.dataset.time || "";
    const date = el.dataset.date || ""; // this might be display string or ISO
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
    
    // Mark details as not empty
    const card = detail.querySelector('.week-details-card');
    if (card) card.setAttribute('data-empty', 'false');

    // Mobile: Open Bottom Sheet
    if (window.innerWidth <= 768) {
      detail.classList.add('is-open');
    }
  }

  if (agenda) {
    agenda.addEventListener("click", (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      const item = target.closest(".week-event-item");
      if (item) {
        const isModified = e.metaKey || e.ctrlKey || e.shiftKey || e.altKey;
        setDetailsFromEl(item);
        if (!isModified) {
          e.preventDefault();
        }
      }
    });
  }

  // Week navigation for events
  const weekPrev = document.getElementById("js-week-prev");
  const weekNext = document.getElementById("js-week-next");
  const weekLabel = document.getElementById("js-week-label");
  const weekOffsetInput = document.getElementById("js-week-offset");
  
  let currentWeekOffset = 0;
  
  async function fetchWeekEvents(offset) {
    if (!agenda) return;
    try {
      const resp = await fetch(`/api/events/week?offset=${encodeURIComponent(offset)}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      
      // Update week label
      if (weekLabel) {
        weekLabel.textContent = `Week of ${data.week_start_date}`;
      }
      
      // Update agenda
      agenda.innerHTML = "";
      data.week_grid.forEach(day => {
        const col = document.createElement("div");
        col.className = "week-day-column";

        const header = document.createElement("div");
        header.className = "week-day-header";
        header.textContent = day.label;
        
        const body = document.createElement("div");
        body.className = "week-day-body";
        
        if (day.items && day.items.length > 0) {
          day.items.forEach(it => {
            const btn = document.createElement("button");
            btn.className = "week-event-item";
            btn.type = "button";
            btn.setAttribute("data-title", it.title || "");
            btn.setAttribute("data-time", it.time || "");
            btn.setAttribute("data-link", it.link || "");
            btn.setAttribute("data-location", it.location || "");
            btn.setAttribute("data-source", it.source || "");
            btn.setAttribute("data-date", it.date || "");
            btn.setAttribute("data-summary", (it.summary || "").replace(/"/g, "&quot;"));
            
            const timeDiv = document.createElement("div");
            timeDiv.className = "week-event-time";
            timeDiv.textContent = it.time || "";
            
            const titleDiv = document.createElement("div");
            titleDiv.className = "week-event-title";
            titleDiv.textContent = it.title || "";
            
            btn.appendChild(timeDiv);
            btn.appendChild(titleDiv);
            body.appendChild(btn);
          });
        } else {
            const empty = document.createElement("div");
            empty.className = "week-day-empty";
            empty.textContent = "—";
            body.appendChild(empty);
        }
        
        col.appendChild(header);
        col.appendChild(body);
        agenda.appendChild(col);
      });
      
      const card = detail ? detail.querySelector('.week-details-card') : null;
      if (card) {
           if (dTitle) dTitle.textContent = "Select an event";
           if (dSummary) dSummary.textContent = "";
           if (dWhen) dWhen.textContent = "—";
           if (dWhere) dWhere.textContent = "—";
           if (dSource) dSource.textContent = "—";
           if (dLink) dLink.style.display = "none";
           card.setAttribute('data-empty', 'true');
      }

    } catch (err) {
      console.error("Failed to fetch week events:", err);
    }
  }
  
  if (weekPrev && weekNext) {
    weekPrev.addEventListener("click", () => {
      currentWeekOffset = Math.max(-4, currentWeekOffset - 1);
      if (weekOffsetInput) weekOffsetInput.value = currentWeekOffset;
      fetchWeekEvents(currentWeekOffset);
    });
    
    weekNext.addEventListener("click", () => {
      currentWeekOffset = Math.min(4, currentWeekOffset + 1);
      if (weekOffsetInput) weekOffsetInput.value = currentWeekOffset;
      fetchWeekEvents(currentWeekOffset);
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

  // Compressed weather widget (similar to tides)
  const weatherOutput = document.getElementById("js-weather-output");
  const weatherUnitsSelect = document.getElementById("js-units");
  
  function toC(f) {
    return (f - 32) * 5 / 9;
  }
  function fmt(n) {
    return Math.round(n);
  }
  
  function updateWeatherDisplay() {
    if (!weatherOutput) return;
    const units = weatherUnitsSelect ? (weatherUnitsSelect.value || "F") : "F";
    
    // Get weather data from data attributes or window
    const weatherData = window.WEATHER_DATA || {};
    const daypartData = window.DAYPART_TEMPS || {};
    const timeStr = window.TIME_STR || "";
    const weatherDesc = weatherData.weather_desc || "";
    
    const currentTemp = weatherData.current_temp;
    const highTemp = weatherData.high_temp;
    const lowTemp = weatherData.low_temp;
    
    const parts = [];
    
    // Time and condition
    if (timeStr && weatherDesc) {
      parts.push(`${timeStr} · ${weatherDesc}`);
    }
    
    // Current temp
    if (currentTemp != null && currentTemp !== null) {
      const temp = units === "F" ? currentTemp : toC(currentTemp);
      parts.push(`${fmt(temp)}°`);
    }

    // Update Mobile Header Status
    const mobileStatus = document.getElementById('js-mobile-status-text');
    if (mobileStatus) {
        const now = new Date();
        const dateStr = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        const t = (currentTemp != null) ? `${fmt(units === "F" ? currentTemp : toC(currentTemp))}°` : '';
        const d = weatherDesc ? weatherDesc : '';
        mobileStatus.textContent = `${dateStr} · ${t} ${d}`;
    }
    
    // High/Low
    if (highTemp != null && highTemp !== null && lowTemp != null && lowTemp !== null) {
      const hi = units === "F" ? highTemp : toC(highTemp);
      const lo = units === "F" ? lowTemp : toC(lowTemp);
      parts.push(`H ${fmt(hi)}° L ${fmt(lo)}°`);
    }
    
    // Dayparts
    const dayparts = [];
    if (daypartData.morning != null && daypartData.morning !== null) {
      const m = units === "F" ? daypartData.morning : toC(daypartData.morning);
      dayparts.push(`Morning ${fmt(m)}°`);
    }
    if (daypartData.afternoon != null && daypartData.afternoon !== null) {
      const a = units === "F" ? daypartData.afternoon : toC(daypartData.afternoon);
      dayparts.push(`Afternoon ${fmt(a)}°`);
    }
    if (daypartData.evening != null && daypartData.evening !== null) {
      const e = units === "F" ? daypartData.evening : toC(daypartData.evening);
      dayparts.push(`Evening ${fmt(e)}°`);
    }
    if (daypartData.night != null && daypartData.night !== null) {
      const n = units === "F" ? daypartData.night : toC(daypartData.night);
      dayparts.push(`Night ${fmt(n)}°`);
    }
    
    if (dayparts.length > 0) {
      parts.push(dayparts.join(" "));
    }
    
    weatherOutput.textContent = parts.length > 0 ? parts.join("  ·  ") : "Weather unavailable.";
  }
  
  if (weatherUnitsSelect) {
    try {
      const saved = localStorage.getItem("units");
      if (saved && (saved === "F" || saved === "C")) {
        weatherUnitsSelect.value = saved;
      }
    } catch {}
    weatherUnitsSelect.addEventListener("change", updateWeatherDisplay);
  }
  
  // Wait for window data to be available
  if (window.WEATHER_DATA) {
    updateWeatherDisplay();
  } else {
    // Retry after a short delay
    setTimeout(updateWeatherDisplay, 100);
  }

  // --- MOBILE LOGIC ---

  // 1. Accordion Toggles
  const toggles = document.querySelectorAll('.ecd-mobile-accordion-toggle');
  toggles.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('aria-controls');
      const target = document.getElementById(targetId);
      if (target) {
        const isExpanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', !isExpanded);
        target.classList.toggle('is-open', !isExpanded);
      }
    });
  });

  // 2. Mobile Week Scroller & Events
  const weekData = window.WEEK_GRID || [];
  const mobileWeekScroll = document.getElementById('js-mobile-week-scroll');
  const mobileEventsToday = document.getElementById('js-mobile-events-today');
  
  // Calculate today YYYY-MM-DD
  const now = new Date();
  const todayStr = now.toLocaleDateString('en-CA'); // YYYY-MM-DD in local time usually, or close enough
  
  if (mobileWeekScroll && weekData.length > 0) {
    weekData.forEach((day, index) => {
      const pill = document.createElement('button');
      pill.className = 'ecd-day-pill';
      pill.type = 'button';
      pill.textContent = day.label; // "Mon", "Tue"
      if (index === 0) pill.classList.add('is-selected'); // Default to first day? Or today?
      
      // Better: check if label matches today's day name, or passed date
      // We don't have exact date in week_grid items easily accessible at top level, 
      // but assuming week starts Monday or current week.
      // Let's just default to first day or highlighting logic if we had dates.
      
      pill.addEventListener('click', () => {
        // Highlight pill
        document.querySelectorAll('.ecd-day-pill').forEach(p => p.classList.remove('is-selected'));
        pill.classList.add('is-selected');
        
        // Filter events (Not implemented fully in Step 4, 
        // prompt said "Show only that day’s events in the 'Today / Selected Day' events list")
        // Implementation: Filter existing cards in 'This Week' or just rely on 'This Week' list?
        // Step 4 says: "When a user taps... Show only that day’s events in the 'Today / Selected Day' events list"
        
        // Let's filter the "This Week" list to only show selected day? 
        // OR update the "Today" section to become "Selected Day".
        const sectionTitle = document.querySelector('.ecd-mobile-events .ecd-section-heading');
        if (sectionTitle) sectionTitle.textContent = day.label;
        
        mobileEventsToday.innerHTML = '';
        if (day.items && day.items.length > 0) {
           day.items.forEach(it => {
               const card = createEventCard(it);
               mobileEventsToday.appendChild(card);
           });
        } else {
            mobileEventsToday.innerHTML = '<div style="font-size:12px; color:var(--muted-ink); padding:8px;">No events.</div>';
        }
      });
      
      mobileWeekScroll.appendChild(pill);
    });

    // Initial populate of "Today" (using first day of week grid as default, or actual today if found)
    // We already have "This Week" populated in template.
    // Let's populate "Today" with actual today's events if possible.
    // We can look at the rendered "This Week" cards and find today's date.
    
    const allMobileCards = document.querySelectorAll('.ecd-mobile-events-week .ecd-event-card');
    let todayFound = false;
    allMobileCards.forEach(card => {
        // card.dataset.date is "YYYY-MM-DD ..." or similar
        if (card.dataset.date && card.dataset.date.includes(todayStr)) {
            const clone = card.cloneNode(true);
            clone.addEventListener('click', (e) => handleMobileCardClick(e, clone));
            mobileEventsToday.appendChild(clone);
            todayFound = true;
        }
    });
    if (!todayFound) {
        mobileEventsToday.innerHTML = '<div style="font-size:12px; color:var(--muted-ink); padding:8px;">No events today.</div>';
    }

    // Attach click listeners to "This Week" cards too
    allMobileCards.forEach(card => {
        card.addEventListener('click', (e) => handleMobileCardClick(e, card));
    });
  }

  function createEventCard(it) {
      const art = document.createElement('article');
      art.className = 'ecd-event-card';
      art.dataset.title = it.title;
      art.dataset.summary = it.summary;
      art.dataset.time = it.time;
      art.dataset.location = it.location;
      art.dataset.source = it.source;
      art.dataset.link = it.link;
      
      art.innerHTML = `
        <div class="ecd-event-time">${it.time}</div>
        <div class="ecd-event-title">${it.title}</div>
        <div class="ecd-event-meta">${it.location || ''}</div>
      `;
      art.addEventListener('click', (e) => handleMobileCardClick(e, art));
      return art;
  }

  function handleMobileCardClick(e, card) {
      setDetailsFromEl(card);
  }

  // 3. Details Bottom Sheet Close
  const closeDetails = document.getElementById('js-details-close');
  if (closeDetails) {
      closeDetails.addEventListener('click', () => {
          detail.classList.remove('is-open');
      });
  }
});
