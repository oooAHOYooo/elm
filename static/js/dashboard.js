/**
 * Elm City Daily — Dashboard JavaScript (MVP)
 * Simplified interactions for the newspaper-style dashboard
 */

(function() {
    'use strict';

    // ==========================================================================
    // DARK MODE
    // ==========================================================================
    const darkToggle = document.getElementById('js-dark-toggle');
    const themeIcon = document.getElementById('js-theme-icon');
    
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (themeIcon) {
            themeIcon.textContent = theme === 'dark' ? '☀' : '☾';
        }
    }
    
    function initTheme() {
        const saved = localStorage.getItem('theme');
        if (saved) {
            setTheme(saved);
        } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setTheme('dark');
        }
    }
    
    if (darkToggle) {
        darkToggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }
    
    initTheme();

    // ==========================================================================
    // MAP INITIALIZATION
    // ==========================================================================
    const mapFrame = document.getElementById('js-map-frame');
    if (mapFrame) {
        const lat = mapFrame.dataset.lat || '41.3083';
        const lon = mapFrame.dataset.lon || '-72.9279';
        mapFrame.src = `https://www.openstreetmap.org/export/embed.html?bbox=${parseFloat(lon)-0.03}%2C${parseFloat(lat)-0.02}%2C${parseFloat(lon)+0.03}%2C${parseFloat(lat)+0.02}&layer=mapnik&marker=${lat}%2C${lon}`;
    }

    // ==========================================================================
    // TIDES
    // ==========================================================================
    async function loadTides() {
        const output = document.getElementById('js-tide-output');
        if (!output) return;
        
        try {
            const res = await fetch('/api/tides?date=today');
            if (!res.ok) throw new Error('Failed to fetch tides');
            const data = await res.json();
            
            if (data.predictions && data.predictions.length > 0) {
                const html = data.predictions.map(p => {
                    const time = p.t ? p.t.split(' ')[1] : '';
                    const height = parseFloat(p.v).toFixed(1);
                    const type = p.type === 'H' ? 'High' : 'Low';
                    return `<div><strong>${type}</strong> ${time} · ${height} ft</div>`;
                }).join('');
                output.innerHTML = html;
            } else {
                output.textContent = 'No tide data available';
            }
        } catch (e) {
            output.textContent = 'Tide data unavailable';
        }
    }
    
    loadTides();

    // ==========================================================================
    // EVENT DETAIL PANEL
    // ==========================================================================
    const detailTitle = document.getElementById('js-detail-title');
    const detailWhen = document.getElementById('js-detail-when');
    const detailWhere = document.getElementById('js-detail-where');
    const detailSource = document.getElementById('js-detail-source');
    const detailSummary = document.getElementById('js-detail-summary');
    const detailLink = document.getElementById('js-detail-link');
    const detailCard = document.querySelector('.event-detail__card');
    
    function showEventDetail(data) {
        if (!detailTitle) return;
        
        detailTitle.textContent = data.title || 'Event';
        detailWhen.textContent = data.date || data.time || '—';
        detailWhere.textContent = data.location || '—';
        detailSource.textContent = data.source || '—';
        detailSummary.textContent = data.summary || '';
        
        if (data.link && data.link !== '#') {
            detailLink.href = data.link;
            detailLink.style.display = 'inline';
        } else {
            detailLink.style.display = 'none';
        }
        
        if (detailCard) {
            detailCard.dataset.empty = 'false';
        }
    }
    
    // Event chip click handlers
    document.querySelectorAll('.event-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            showEventDetail({
                title: chip.dataset.title,
                time: chip.dataset.time,
                date: chip.dataset.date,
                location: chip.dataset.location,
                source: chip.dataset.source,
                summary: chip.dataset.summary,
                link: chip.dataset.link,
            });
        });
    });

    // ==========================================================================
    // WEEK NAVIGATION
    // ==========================================================================
    const weekPrev = document.getElementById('js-week-prev');
    const weekNext = document.getElementById('js-week-next');
    const weekLabel = document.getElementById('js-week-label');
    const weekOffsetInput = document.getElementById('js-week-offset');
    const calendarGrid = document.getElementById('js-agenda-week');
    
    async function loadWeek(offset) {
        if (!calendarGrid) return;
        
        calendarGrid.classList.add('loading');
        
        try {
            const res = await fetch(`/api/events/week?offset=${offset}`);
            if (!res.ok) throw new Error('Failed');
            const data = await res.json();
            
            if (weekLabel) {
                weekLabel.textContent = `Week of ${data.week_start_date}`;
            }
            if (weekOffsetInput) {
                weekOffsetInput.value = data.week_offset;
            }
            
            // Rebuild calendar grid
            calendarGrid.innerHTML = data.week_grid.map(day => `
                <div class="calendar-day">
                    <div class="calendar-day__header">${day.label}</div>
                    <div class="calendar-day__events">
                        ${day.items.length > 0 ? day.items.map(it => `
                            <button class="event-chip" type="button"
                                data-title="${escapeHtml(it.title)}"
                                data-time="${escapeHtml(it.time)}"
                                data-link="${escapeHtml(it.link)}"
                                data-location="${escapeHtml(it.location)}"
                                data-source="${escapeHtml(it.source)}"
                                data-date="${escapeHtml(it.date)}"
                                data-summary="${escapeHtml(it.summary)}">
                                <span class="event-chip__time">${escapeHtml(it.time)}</span>
                                <span class="event-chip__title">${escapeHtml(truncate(it.title, 35))}</span>
                            </button>
                        `).join('') : '<span class="calendar-day__empty">—</span>'}
                    </div>
                </div>
            `).join('');
            
            // Re-bind click handlers
            calendarGrid.querySelectorAll('.event-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    showEventDetail({
                        title: chip.dataset.title,
                        time: chip.dataset.time,
                        date: chip.dataset.date,
                        location: chip.dataset.location,
                        source: chip.dataset.source,
                        summary: chip.dataset.summary,
                        link: chip.dataset.link,
                    });
                });
            });
        } catch (e) {
            console.error('Failed to load week:', e);
        } finally {
            calendarGrid.classList.remove('loading');
        }
    }
    
    if (weekPrev) {
        weekPrev.addEventListener('click', () => {
            const current = parseInt(weekOffsetInput?.value || '0', 10);
            loadWeek(current - 1);
        });
    }
    
    if (weekNext) {
        weekNext.addEventListener('click', () => {
            const current = parseInt(weekOffsetInput?.value || '0', 10);
            loadWeek(current + 1);
        });
    }

    // ==========================================================================
    // REFRESH
    // ==========================================================================
    const refreshBtn = document.getElementById('js-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            window.location.reload();
        });
    }

    // ==========================================================================
    // UTILITIES
    // ==========================================================================
    function escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
    
    function truncate(str, len) {
        if (!str) return '';
        return str.length > len ? str.slice(0, len) + '…' : str;
    }

    // ==========================================================================
    // POPUP PANELS
    // ==========================================================================
    const overlay = document.getElementById('popup-overlay');
    const popupPanels = document.querySelectorAll('.popup-panel');
    const quickLinks = document.querySelectorAll('.quick-link');
    
    function openPopup(popupId) {
        const panel = document.getElementById(`popup-${popupId}`);
        if (!panel) return;
        
        overlay?.classList.add('active');
        panel.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeAllPopups() {
        overlay?.classList.remove('active');
        popupPanels.forEach(p => p.classList.remove('active'));
        document.body.style.overflow = '';
    }
    
    // Quick link click handlers
    quickLinks.forEach(link => {
        link.addEventListener('click', () => {
            const popupId = link.dataset.popup;
            if (popupId) openPopup(popupId);
        });
    });
    
    // Close button handlers
    document.querySelectorAll('.popup-close').forEach(btn => {
        btn.addEventListener('click', closeAllPopups);
    });
    
    // Overlay click to close
    overlay?.addEventListener('click', closeAllPopups);
    
    // ==========================================================================
    // KEYBOARD SHORTCUTS
    // ==========================================================================
    document.addEventListener('keydown', (e) => {
        // Escape closes popups
        if (e.key === 'Escape') {
            closeAllPopups();
            return;
        }
        
        // Ignore if typing in input
        if (e.target.matches('input, textarea, select')) return;
        
        switch (e.key.toLowerCase()) {
            case 'd':
                darkToggle?.click();
                break;
            case 'r':
                refreshBtn?.click();
                break;
        }
    });

})();
