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
    // EVENT DETAIL DRAWER
    // ==========================================================================
    const eventDrawer = document.getElementById('js-event-drawer');
    const drawerOverlay = document.getElementById('js-drawer-overlay');
    const drawerClose = document.getElementById('js-drawer-close');
    const drawerTitle = document.getElementById('js-drawer-title');
    const drawerTime = document.getElementById('js-drawer-time');
    const drawerLocation = document.getElementById('js-drawer-location');
    const drawerSource = document.getElementById('js-drawer-source');
    const drawerDescription = document.getElementById('js-drawer-description');
    const drawerFooter = document.getElementById('js-drawer-footer');
    const drawerLink = document.getElementById('js-drawer-link');
    
    function openEventDrawer(data) {
        if (!eventDrawer) return;
        
        // Update drawer content with sentence case
        if (drawerTitle) {
            drawerTitle.textContent = toSentenceCasePreserveAcronyms(data.title || 'Event');
        }
        
        if (drawerTime) {
            const timeSpan = drawerTime.querySelector('span');
            if (timeSpan) {
                const timeValue = formatTime(data.time || data.date || '');
                timeSpan.textContent = timeValue || '—';
            }
        }
        
        if (drawerLocation) {
            const locationSpan = drawerLocation.querySelector('span');
            if (locationSpan && data.location) {
                locationSpan.textContent = toSentenceCasePreserveAcronyms(data.location);
                drawerLocation.style.display = 'block';
            } else {
                drawerLocation.style.display = 'none';
            }
        }
        
        if (drawerSource) {
            const sourceSpan = drawerSource.querySelector('span');
            if (sourceSpan && data.source) {
                sourceSpan.textContent = toSentenceCasePreserveAcronyms(data.source);
                drawerSource.style.display = 'block';
            } else {
                drawerSource.style.display = 'none';
            }
        }
        
        if (drawerDescription) {
            const descText = data.summary || '';
            drawerDescription.textContent = descText ? toSentenceCasePreserveAcronyms(descText) : 'No description available.';
            drawerDescription.style.display = descText ? 'block' : 'none';
        }
        
        // Show/hide link
        if (data.link && data.link !== '#' && data.link !== '') {
            if (drawerLink) {
                drawerLink.href = data.link;
            }
            if (drawerFooter) {
                drawerFooter.style.display = 'block';
            }
        } else {
            if (drawerFooter) {
                drawerFooter.style.display = 'none';
            }
        }
        
        // Show drawer
        eventDrawer.setAttribute('aria-hidden', 'false');
        eventDrawer.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus management
        if (drawerClose) {
            drawerClose.focus();
        }
    }
    
    function closeEventDrawer() {
        if (!eventDrawer) return;
        eventDrawer.setAttribute('aria-hidden', 'true');
        eventDrawer.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    // Close drawer handlers
    if (drawerOverlay) {
        drawerOverlay.addEventListener('click', closeEventDrawer);
    }
    
    if (drawerClose) {
        drawerClose.addEventListener('click', closeEventDrawer);
    }
    
    // Keyboard: Escape closes drawer (handled in main keyboard handler below)
    
    // Convert initial page load events to sentence case
    function convertInitialEvents() {
        document.querySelectorAll('.event-card').forEach(card => {
            const titleEl = card.querySelector('.event-card__title');
            const locationEl = card.querySelector('.event-card__location');
            const descEl = card.querySelector('.event-card__description');
            
            if (titleEl && titleEl.textContent) {
                titleEl.textContent = toSentenceCasePreserveAcronyms(titleEl.textContent);
            }
            if (locationEl && locationEl.textContent) {
                locationEl.textContent = toSentenceCasePreserveAcronyms(locationEl.textContent);
            }
            if (descEl && descEl.textContent) {
                descEl.textContent = toSentenceCasePreserveAcronyms(descEl.textContent);
            }
        });
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', convertInitialEvents);
    } else {
        convertInitialEvents();
    }
    
    // Event card click handlers (delegated)
    document.addEventListener('click', (e) => {
        const eventCard = e.target.closest('.event-card');
        if (eventCard) {
            openEventDrawer({
                title: eventCard.dataset.title || '',
                time: eventCard.dataset.time || '',
                date: eventCard.dataset.date || '',
                location: eventCard.dataset.location || '',
                source: eventCard.dataset.source || '',
                summary: eventCard.dataset.summary || '',
                link: eventCard.dataset.link || '',
            });
        }
    });
    
    // Keyboard: Enter/Space on event card
    document.addEventListener('keydown', (e) => {
        if (e.target.classList.contains('event-card') && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            e.target.click();
        }
    });

    // ==========================================================================
    // WEEK NAVIGATION
    // ==========================================================================
    const weekPrev = document.getElementById('js-week-prev');
    const weekNext = document.getElementById('js-week-next');
    const weekLabel = document.getElementById('js-week-label');
    const weekOffsetInput = document.getElementById('js-week-offset');
    const eventsList = document.getElementById('js-agenda-week');
    
    async function loadWeek(offset) {
        if (!eventsList) return;
        
        eventsList.classList.add('loading');
        
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
            
            // Rebuild events list with cards
            eventsList.innerHTML = data.week_grid.map(day => {
                const dayLabel = day.label || '';
                const hasEvents = day.items && day.items.length > 0;
                
                return `
                    <div class="events-day-group">
                        <h3 class="events-day-group__header">${escapeHtml(dayLabel)}</h3>
                        <div class="events-day-group__cards">
                            ${hasEvents ? day.items.map(it => {
                                const title = toSentenceCasePreserveAcronyms(it.title || 'Event');
                                const time = formatTime(it.time || '');
                                const location = it.location ? toSentenceCasePreserveAcronyms(it.location) : '';
                                const summary = it.summary ? toSentenceCasePreserveAcronyms(it.summary) : '';
                                
                                return `
                                    <article class="event-card" tabindex="0" role="button"
                                        aria-label="Event: ${escapeHtml(title)}"
                                        data-title="${escapeHtml(it.title || '')}"
                                        data-time="${escapeHtml(it.time || '')}"
                                        data-link="${escapeHtml(it.link || '')}"
                                        data-location="${escapeHtml(it.location || '')}"
                                        data-source="${escapeHtml(it.source || '')}"
                                        data-date="${escapeHtml(it.date || '')}"
                                        data-summary="${escapeHtml(it.summary || '')}">
                                        <div class="event-card__time">
                                            <span class="event-card__time-value">${escapeHtml(time)}</span>
                                            <span class="event-card__day-label">${escapeHtml(dayLabel)}</span>
                                        </div>
                                        <div class="event-card__content">
                                            <h4 class="event-card__title">${escapeHtml(title)}</h4>
                                            ${location ? `<p class="event-card__location">${escapeHtml(location)}</p>` : ''}
                                            ${summary ? `<p class="event-card__description">${escapeHtml(truncate(summary, 80))}</p>` : ''}
                                            <button class="event-card__more" aria-label="View more details">More details →</button>
                                        </div>
                                    </article>
                                `;
                            }).join('') : '<p class="events-day-group__empty">— No public events listed</p>'}
                        </div>
                    </div>
                `;
            }).join('');
        } catch (e) {
            console.error('Failed to load week:', e);
            eventsList.innerHTML = '<p class="events-error">Unable to load events. Please try again later.</p>';
        } finally {
            eventsList.classList.remove('loading');
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

    /**
     * Convert string to sentence case while preserving acronyms
     * Examples: "CONCERT ON THE GREEN" -> "Concert on the green"
     *           "CT TRANSIT" -> "CT Transit"
     *           "NWS ALERTS" -> "NWS Alerts"
     */
    function toSentenceCasePreserveAcronyms(str) {
        if (!str) return '';
        
        // Split by spaces and process each word
        return str.split(/\s+/).map((word, index) => {
            // If word is all caps and 2-4 chars, likely an acronym
            if (word.length >= 2 && word.length <= 4 && /^[A-Z0-9]+$/.test(word)) {
                return word; // Keep acronym as-is
            }
            
            // First word: capitalize first letter, lowercase rest
            // Other words: lowercase unless it's an acronym
            if (index === 0) {
                return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
            } else {
                return word.toLowerCase();
            }
        }).join(' ');
    }

    /**
     * Format time string to human-friendly format
     * Handles various input formats: "7:00 PM", "19:00", "2025-12-25 07:00 PM"
     */
    function formatTime(timeStr) {
        if (!timeStr) return '';
        
        // If already in "7:00 PM" format, return as-is
        if (/^\d{1,2}:\d{2}\s*(AM|PM)$/i.test(timeStr.trim())) {
            return timeStr.trim();
        }
        
        // Try to parse ISO datetime or other formats
        try {
            const date = new Date(timeStr);
            if (!isNaN(date.getTime())) {
                return date.toLocaleTimeString('en-US', { 
                    hour: 'numeric', 
                    minute: '2-digit',
                    hour12: true 
                });
            }
        } catch (e) {
            // Fall through to return original
        }
        
        return timeStr;
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
        // Escape closes popups and event drawer
        if (e.key === 'Escape') {
            if (eventDrawer && eventDrawer.classList.contains('active')) {
                closeEventDrawer();
            } else {
                closeAllPopups();
            }
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

    // ==========================================================================
    // LAST UPDATED TIMESTAMP
    // ==========================================================================
    const lastUpdatedEl = document.getElementById('js-last-updated');
    const pageLoadTime = Date.now();
    
    function updateFreshness() {
        if (!lastUpdatedEl) return;
        const mins = Math.floor((Date.now() - pageLoadTime) / 60000);
        if (mins < 1) {
            lastUpdatedEl.textContent = 'Updated just now';
        } else if (mins === 1) {
            lastUpdatedEl.textContent = 'Updated 1 minute ago';
        } else {
            lastUpdatedEl.textContent = `Updated ${mins} minutes ago`;
        }
    }
    
    setInterval(updateFreshness, 60000);

})();
