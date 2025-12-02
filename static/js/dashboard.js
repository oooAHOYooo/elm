document.addEventListener("DOMContentLoaded", () => {
  const checkboxes = Array.from(document.querySelectorAll(".js-filter"));
  const cards = Array.from(document.querySelectorAll(".card"));

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
});


