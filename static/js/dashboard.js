/**
 * Elm City Daily — Dashboard JavaScript (MVP)
 * Simplified interactions for the newspaper-style dashboard
 */

(function() {
    'use strict';
    
    // Update loading progress when tides load
    function updateLoadingProgress(percent, message) {
        var splash = document.getElementById('loading-splash');
        if (!splash || splash.classList.contains('loading-splash--hidden')) return;
        
        var progressBar = document.getElementById('loading-progress');
        var percentage = document.getElementById('loading-percentage');
        var messageEl = document.getElementById('loading-message');
        
        if (progressBar) progressBar.style.width = percent + '%';
        if (percentage) percentage.textContent = Math.floor(percent) + '%';
        if (messageEl && message) messageEl.textContent = message;
    }

    // ==========================================================================
    // LIVE CLOCK
    // ==========================================================================
    function updateClock() {
        const clockEl = document.getElementById('js-clock');
        if (!clockEl) return;
        
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const seconds = now.getSeconds().toString().padStart(2, '0');
        clockEl.textContent = `${hours}:${minutes}:${seconds}`;
    }
    
    // Update clock immediately and then every second
    updateClock();
    setInterval(updateClock, 1000);

    // ==========================================================================
    // MOON PHASES
    // ==========================================================================
    function calculateMoonPhase(date) {
        // Calculate moon phase (0 = new moon, 0.5 = full moon, 1 = new moon again)
        // Using a simplified algorithm based on days since known new moon
        // Reference: January 11, 2024 was a new moon
        const referenceNewMoon = new Date('2024-01-11T00:00:00Z');
        const daysSinceReference = (date - referenceNewMoon) / (1000 * 60 * 60 * 24);
        const lunarCycle = 29.53; // days in a lunar cycle
        const phase = (daysSinceReference % lunarCycle) / lunarCycle;
        return phase;
    }

    function getMoonPhaseName(phase) {
        if (phase < 0.03 || phase > 0.97) return 'New Moon';
        if (phase < 0.22) return 'Waxing Crescent';
        if (phase < 0.28) return 'First Quarter';
        if (phase < 0.47) return 'Waxing Gibbous';
        if (phase < 0.53) return 'Full Moon';
        if (phase < 0.72) return 'Waning Gibbous';
        if (phase < 0.78) return 'Last Quarter';
        return 'Waning Crescent';
    }

    function getMoonPhaseIcon(phase) {
        // Return CSS class name for moon phase icon
        if (phase < 0.03 || phase > 0.97) return 'moon-phase__icon--new';
        if (phase < 0.22) return 'moon-phase__icon--waxing-crescent';
        if (phase < 0.28) return 'moon-phase__icon--first-quarter';
        if (phase < 0.47) return 'moon-phase__icon--waxing-gibbous';
        if (phase < 0.53) return 'moon-phase__icon--full';
        if (phase < 0.72) return 'moon-phase__icon--waning-gibbous';
        if (phase < 0.78) return 'moon-phase__icon--last-quarter';
        return 'moon-phase__icon--waning-crescent';
    }

    function updateMoonPhases() {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const day3 = new Date(today);
        day3.setDate(day3.getDate() + 2);

        const phases = [
            { date: today, iconEl: document.getElementById('js-moon-today'), nameEl: document.getElementById('js-moon-name-today') },
            { date: tomorrow, iconEl: document.getElementById('js-moon-tomorrow'), nameEl: document.getElementById('js-moon-name-tomorrow') },
            { date: day3, iconEl: document.getElementById('js-moon-day3'), nameEl: document.getElementById('js-moon-name-day3') }
        ];

        phases.forEach(({ date, iconEl, nameEl }) => {
            if (!iconEl || !nameEl) return;
            
            const phase = calculateMoonPhase(date);
            const phaseName = getMoonPhaseName(phase);
            const iconClass = getMoonPhaseIcon(phase);
            
            iconEl.className = 'moon-phase__icon ' + iconClass;
            nameEl.textContent = phaseName;
        });

        // Update day 3 label
        const day3Label = document.getElementById('js-moon-label-day3');
        if (day3Label) {
            const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            day3Label.textContent = dayNames[day3.getDay()];
        }
    }

    updateMoonPhases();

    // ==========================================================================
    // DARK MODE
    // ==========================================================================
    const darkToggle = document.getElementById('js-dark-toggle');
    const themeIcon = document.getElementById('js-theme-icon');
    
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'theme-icon theme-icon--sun' : 'theme-icon theme-icon--moon';
            themeIcon.textContent = '';
        }
    }
    
    function initTheme() {
        const saved = localStorage.getItem('theme');
        if (saved) {
            setTheme(saved);
        } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setTheme('dark');
        } else {
            // Initialize icon even if no theme is set
            if (themeIcon) {
                const current = document.documentElement.getAttribute('data-theme') || 'light';
                themeIcon.className = current === 'dark' ? 'theme-icon theme-icon--sun' : 'theme-icon theme-icon--moon';
                themeIcon.textContent = '';
            }
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
    function parseTideTime(timeStr) {
        if (!timeStr) return null;
        try {
            const parts = timeStr.split(' ');
            if (parts.length >= 2) {
                const timePart = parts[1];
                const [hours, minutes] = timePart.split(':').map(Number);
                return { hours, minutes };
            }
        } catch (e) {
            return null;
        }
        return null;
    }

    function getCurrentTideStatus(predictions) {
        if (!predictions || predictions.length === 0) return null;
        
        const now = new Date();
        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();
        const currentTimeMinutes = currentHour * 60 + currentMinute;
        
        // Sort predictions by time
        const sorted = [...predictions].sort((a, b) => {
            const timeA = parseTideTime(a.t);
            const timeB = parseTideTime(b.t);
            if (!timeA || !timeB) return 0;
            const minutesA = timeA.hours * 60 + timeA.minutes;
            const minutesB = timeB.hours * 60 + timeB.minutes;
            return minutesA - minutesB;
        });
        
        // Find where we are in the tide cycle
        for (let i = 0; i < sorted.length; i++) {
            const tide = sorted[i];
            const tideTime = parseTideTime(tide.t);
            if (!tideTime) continue;
            
            const tideMinutes = tideTime.hours * 60 + tideTime.minutes;
            const nextTide = sorted[i + 1];
            
            if (tideMinutes <= currentTimeMinutes && (!nextTide || parseTideTime(nextTide.t).hours * 60 + parseTideTime(nextTide.t).minutes > currentTimeMinutes)) {
                const isHigh = tide.type === 'H';
                const nextIsHigh = nextTide ? nextTide.type === 'H' : !isHigh;
                
                if (isHigh && !nextIsHigh) {
                    return { status: 'falling', nextTide: nextTide, currentTide: tide };
                } else if (!isHigh && nextIsHigh) {
                    return { status: 'rising', nextTide: nextTide, currentTide: tide };
                }
            }
        }
        
        // Default to first tide
        if (sorted.length > 0) {
            const first = sorted[0];
            const firstTime = parseTideTime(first.t);
            if (firstTime) {
                const firstMinutes = firstTime.hours * 60 + firstTime.minutes;
                if (currentTimeMinutes < firstMinutes) {
                    return { status: 'unknown', nextTide: first, currentTide: null };
                }
            }
        }
        
        return { status: 'unknown', nextTide: sorted[0] || null, currentTide: null };
    }

    function estimateBoatTraffic(predictions) {
        if (!predictions || predictions.length === 0) return { boatsIn: [], boatsOut: [] };
        
        const boatsIn = [];
        const boatsOut = [];
        
        // Boats typically go out during rising tide (after low tide, easier to navigate out)
        // Boats typically come in during falling tide (after high tide, easier to navigate in)
        // Estimate activity windows: 1-2 hours after low tide for going out, 1-2 hours after high tide for coming in
        for (let i = 0; i < predictions.length; i++) {
            const tide = predictions[i];
            const tideTime = parseTideTime(tide.t);
            if (!tideTime) continue;
            
            const timeStr = tide.t ? tide.t.split(' ')[1] : '';
            const height = parseFloat(tide.v).toFixed(1);
            
            if (tide.type === 'L') {
                // Low tide - boats will go out in the next 1-2 hours (rising tide)
                boatsOut.push({
                    time: timeStr,
                    tide: 'Low',
                    height: height,
                    period: 'Rising',
                    activity: '1-2 hours after'
                });
            } else if (tide.type === 'H') {
                // High tide - boats will come in in the next 1-2 hours (falling tide)
                boatsIn.push({
                    time: timeStr,
                    tide: 'High',
                    height: height,
                    period: 'Falling',
                    activity: '1-2 hours after'
                });
            }
        }
        
        return { boatsIn, boatsOut };
    }

    function createTideChart(predictions) {
        if (!predictions || predictions.length === 0) return '';
        
        // Get min and max heights for scaling
        const heights = predictions.map(p => parseFloat(p.v));
        const minHeight = Math.min(...heights);
        const maxHeight = Math.max(...heights);
        const range = maxHeight - minHeight || 1;
        
        // Create 24-hour timeline points
        const points = [];
        const sorted = [...predictions].sort((a, b) => {
            const timeA = parseTideTime(a.t);
            const timeB = parseTideTime(b.t);
            if (!timeA || !timeB) return 0;
            return (timeA.hours * 60 + timeA.minutes) - (timeB.hours * 60 + timeB.minutes);
        });
        
        // Interpolate between tide points for smooth curve
        for (let i = 0; i < sorted.length; i++) {
            const current = sorted[i];
            const next = sorted[i + 1] || sorted[0]; // Wrap around
            const currentTime = parseTideTime(current.t);
            const nextTime = parseTideTime(next.t);
            
            if (!currentTime || !nextTime) continue;
            
            const currentHeight = parseFloat(current.v);
            const nextHeight = parseFloat(next.v);
            const currentMinutes = currentTime.hours * 60 + currentTime.minutes;
            let nextMinutes = nextTime.hours * 60 + nextTime.minutes;
            
            // Handle wrap-around
            if (nextMinutes < currentMinutes) {
                nextMinutes += 24 * 60;
            }
            
            // Add points for this segment
            const segmentLength = nextMinutes - currentMinutes;
            const steps = Math.max(2, Math.floor(segmentLength / 30)); // Points every 30 minutes
            
            for (let j = 0; j <= steps; j++) {
                const t = j / steps;
                // Use sine interpolation for natural tide curve
                const height = currentHeight + (nextHeight - currentHeight) * (0.5 - 0.5 * Math.cos(Math.PI * t));
                const minutes = (currentMinutes + segmentLength * t) % (24 * 60);
                const hours = Math.floor(minutes / 60);
                const mins = minutes % 60;
                
                points.push({
                    time: `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`,
                    height: height,
                    x: (minutes / (24 * 60)) * 100,
                    y: 100 - ((height - minHeight) / range) * 80 // Scale to 80% of height
                });
            }
        }
        
        // Create SVG path
        const pathData = points.map((p, i) => {
            return `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`;
        }).join(' ');
        
        // Get current time position
        const now = new Date();
        const currentMinutes = now.getHours() * 60 + now.getMinutes();
        const currentX = (currentMinutes / (24 * 60)) * 100;
        
        return `
            <div class="tide-chart">
                <svg class="tide-chart__svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <defs>
                        <linearGradient id="tideGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" style="stop-color:#4a90e2;stop-opacity:0.3" />
                            <stop offset="100%" style="stop-color:#4a90e2;stop-opacity:0.1" />
                        </linearGradient>
                    </defs>
                    <path d="${pathData} L 100 100 L 0 100 Z" fill="url(#tideGradient)" />
                    <path d="${pathData}" fill="none" stroke="#4a90e2" stroke-width="0.5" />
                    <line x1="${currentX}" y1="0" x2="${currentX}" y2="100" stroke="#ff6b6b" stroke-width="0.3" stroke-dasharray="1,1" />
                    <circle cx="${currentX}" cy="${points.find(p => Math.abs(parseFloat(p.time.split(':')[0]) * 60 + parseFloat(p.time.split(':')[1]) - currentMinutes) < 30)?.y || 50}" r="1" fill="#ff6b6b" />
                </svg>
                <div class="tide-chart__labels">
                    ${predictions.slice(0, 4).map(p => {
                        const time = p.t ? p.t.split(' ')[1] : '';
                        const height = parseFloat(p.v).toFixed(1);
                        const type = p.type === 'H' ? 'H' : 'L';
                        const timeObj = parseTideTime(p.t);
                        if (!timeObj) return '';
                        const x = ((timeObj.hours * 60 + timeObj.minutes) / (24 * 60)) * 100;
                        return `<span class="tide-chart__label" style="left: ${x}%">
                            <span class="tide-chart__label-time">${time}</span>
                            <span class="tide-chart__label-height">${height}ft</span>
                            <span class="tide-chart__label-type tide-chart__label-type--${type.toLowerCase()}">${type}</span>
                        </span>`;
                    }).join('')}
                </div>
            </div>
        `;
    }

    async function loadTides() {
        const output = document.getElementById('js-tide-output');
        if (!output) return;
        
        updateLoadingProgress(85, 'Loading tide predictions...');
        
        try {
            const res = await fetch('/api/tides?date=today');
            if (!res.ok) throw new Error('Failed to fetch tides');
            const data = await res.json();
            
            updateLoadingProgress(90, 'Finalizing dashboard...');
            
            if (data.predictions && data.predictions.length > 0) {
                const status = getCurrentTideStatus(data.predictions);
                const boatTraffic = estimateBoatTraffic(data.predictions);
                
                // Current status indicator
                let statusHtml = '';
                if (status) {
                    const statusIconClass = status.status === 'rising' ? 'tide-status__icon--rising' : status.status === 'falling' ? 'tide-status__icon--falling' : 'tide-status__icon--stable';
                    const statusText = status.status === 'rising' ? 'Rising' : status.status === 'falling' ? 'Falling' : 'Stable';
                    statusHtml = `
                        <div class="tide-status">
                            <span class="tide-status__icon ${statusIconClass}"></span>
                            <span class="tide-status__text">Tide is ${statusText}</span>
                            ${status.nextTide ? `<span class="tide-status__next">Next: ${status.nextTide.t ? status.nextTide.t.split(' ')[1] : ''} (${status.nextTide.type === 'H' ? 'High' : 'Low'})</span>` : ''}
                        </div>
                    `;
                }
                
                // Tide chart
                const chartHtml = createTideChart(data.predictions);
                
                // Tide list
                const tidesHtml = data.predictions.slice(0, 4).map(p => {
                    const time = p.t ? p.t.split(' ')[1] : '';
                    const height = parseFloat(p.v).toFixed(1);
                    const type = p.type === 'H' ? 'High' : 'Low';
                    return `
                        <div class="tide-item tide-item--${type.toLowerCase()}">
                            <span class="tide-item__icon tide-item__icon--${type.toLowerCase()}"></span>
                            <span class="tide-item__type">${type}</span>
                            <span class="tide-item__time">${time}</span>
                            <span class="tide-item__height">${height} ft</span>
                        </div>
                    `;
                }).join('');
                
                // Boat traffic widget
                const boatsInCount = boatTraffic.boatsIn.length;
                const boatsOutCount = boatTraffic.boatsOut.length;
                const boatsHtml = `
                    <div class="boat-traffic">
                        <h3 class="boat-traffic__title"><span class="boat-traffic__title-icon"></span> Harbor Activity</h3>
                        <div class="boat-traffic__grid">
                            <div class="boat-traffic__item boat-traffic__item--out">
                                <span class="boat-traffic__icon boat-traffic__icon--out"></span>
                                <div class="boat-traffic__content">
                                    <div class="boat-traffic__label">Boats Out</div>
                                    <div class="boat-traffic__count">${boatsOutCount}</div>
                                    ${boatTraffic.boatsOut.length > 0 ? `
                                        <div class="boat-traffic__times">
                                            ${boatTraffic.boatsOut.map(b => `<span class="boat-traffic__time" title="Low tide at ${b.time}, boats typically go out 1-2 hours after">${b.time}</span>`).join('')}
                                        </div>
                                    ` : '<div class="boat-traffic__times"><span class="boat-traffic__time">None today</span></div>'}
                                </div>
                            </div>
                            <div class="boat-traffic__item boat-traffic__item--in">
                                <span class="boat-traffic__icon boat-traffic__icon--in"></span>
                                <div class="boat-traffic__content">
                                    <div class="boat-traffic__label">Boats In</div>
                                    <div class="boat-traffic__count">${boatsInCount}</div>
                                    ${boatTraffic.boatsIn.length > 0 ? `
                                        <div class="boat-traffic__times">
                                            ${boatTraffic.boatsIn.map(b => `<span class="boat-traffic__time" title="High tide at ${b.time}, boats typically come in 1-2 hours after">${b.time}</span>`).join('')}
                                        </div>
                                    ` : '<div class="boat-traffic__times"><span class="boat-traffic__time">None today</span></div>'}
                                </div>
                            </div>
                        </div>
                        <div class="boat-traffic__note">
                            <small>Activity typically occurs 1-2 hours after tide change</small>
                        </div>
                    </div>
                `;
                
                output.innerHTML = `
                    ${statusHtml}
                    ${chartHtml}
                    <div class="tides-list">
                        ${tidesHtml}
                    </div>
                    ${boatsHtml}
                `;
            } else {
                output.textContent = 'No tide data available';
            }
        } catch (e) {
            console.error('Tide loading error:', e);
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
