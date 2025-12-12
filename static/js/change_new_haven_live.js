async function loadChangeNewHaven() {
  try {
    const res = await fetch("/api/change-new-haven-live", { headers: { "Accept": "application/json" } });
    if (!res.ok) throw new Error("Failed");
    const items = await res.json();
    
    // Find or create the dropdown list for City Resources
    const container = document.getElementById("js-city-resources-list");
    const countBadge = document.getElementById("js-city-resources-count");
    
    if (!container) return;
    
    container.innerHTML = "";
    if (countBadge) countBadge.textContent = items.length;

    (items || []).forEach((item) => {
      const li = document.createElement("li");
      li.className = "feed-item";
      li.innerHTML = `
        <a href="${item.url || '#'}" target="_blank" rel="noopener" class="feed-link">
            <span class="feed-title">${(item.title || "").slice(0, 100)}</span>
            <span class="feed-meta">${item.category || "Resource"}</span>
        </a>
      `;
      container.appendChild(li);
    });
  } catch (e) {
    const container = document.getElementById("js-city-resources-list");
    if (container) container.innerHTML = "<li class='feed-item' style='padding:1rem;color:var(--text-muted)'>Unavailable</li>";
  }
}

// Initial load
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadChangeNewHaven);
} else {
    loadChangeNewHaven();
}
setInterval(loadChangeNewHaven, 1800000); // 30 mins



