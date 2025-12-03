/**
 * Traffic Camera Gallery for Elm City Daily
 * Fetches camera data from API and displays in a clickable grid
 */

let trafficCams = [];
let refreshIntervals = {};

/**
 * Fetch camera data from API
 */
async function fetchCameras() {
    try {
        const response = await fetch('/api/cams');
        const data = await response.json();
        trafficCams = data.cameras || [];
        return trafficCams;
    } catch (error) {
        console.error('Failed to fetch cameras:', error);
        return [];
    }
}

/**
 * Build the camera gallery DOM
 */
function buildCamGallery(containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Container not found:', containerId);
        return;
    }

    // Clear existing content
    container.innerHTML = '';

    if (trafficCams.length === 0) {
        container.innerHTML = '<div class="cam-error">No cameras available. Please check back later.</div>';
        return;
    }

    trafficCams.forEach(cam => {
        const card = document.createElement('div');
        card.className = 'cam-card';
        card.setAttribute('data-cam-id', cam.id);
        
        card.innerHTML = `
            <div class="cam-card__image-wrapper">
                <img 
                    src="${cam.thumbnail_url}" 
                    alt="${cam.label}" 
                    id="${cam.id}-img"
                    class="cam-card__image"
                    loading="lazy"
                    onerror="this.src='/static/img/cam-error.png'; this.alt='Camera feed unavailable'"
                >
                <div class="cam-card__overlay">
                    <span class="cam-card__click-hint">Click to view full size</span>
                </div>
            </div>
            <div class="cam-card__info">
                <div class="cam-label">${cam.label}</div>
                <div class="cam-meta">
                    <span class="cam-highway">${cam.highway || ''}</span>
                    ${cam.direction ? `<span class="cam-direction">${cam.direction}</span>` : ''}
                </div>
                <div class="cam-location">${cam.location || ''}</div>
            </div>
        `;

        card.onclick = () => openCamModal(cam);
        card.setAttribute('role', 'button');
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', `View ${cam.label} camera`);
        
        // Keyboard accessibility
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openCamModal(cam);
            }
        });

        container.appendChild(card);

        // Setup image refresh with cache busting
        if (cam.refresh_ms && cam.refresh_ms > 0) {
            const intervalId = setInterval(() => {
                const img = document.getElementById(`${cam.id}-img`);
                if (img) {
                    // Add timestamp to bypass cache
                    const separator = cam.feed_url.includes('?') ? '&' : '?';
                    img.src = `${cam.feed_url}${separator}ts=${Date.now()}`;
                }
            }, cam.refresh_ms);
            
            refreshIntervals[cam.id] = intervalId;
        }
    });
}

/**
 * Open camera modal for full-size view
 */
function openCamModal(cam) {
    // Remove existing modal if present
    const existingModal = document.querySelector('.cam-modal');
    if (existingModal) {
        existingModal.remove();
    }

    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'cam-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-labelledby', 'cam-modal-title');
    modal.setAttribute('aria-modal', 'true');
    
    modal.innerHTML = `
        <div class="cam-modal-content">
            <button class="cam-close" aria-label="Close camera view">&times;</button>
            <h2 id="cam-modal-title" class="cam-modal-title">${cam.label}</h2>
            <div class="cam-modal-meta">
                <span class="cam-modal-highway">${cam.highway || ''}</span>
                ${cam.direction ? `<span class="cam-modal-direction">${cam.direction}</span>` : ''}
                ${cam.location ? `<span class="cam-modal-location">${cam.location}</span>` : ''}
            </div>
            <div class="cam-modal-image-wrapper">
                <img 
                    src="${cam.feed_url}" 
                    alt="${cam.label}" 
                    class="cam-modal-image"
                    id="cam-modal-img-${cam.id}"
                    loading="lazy"
                >
            </div>
            <div class="cam-modal-footer">
                <p class="cam-modal-source">Source: <a href="${cam.source_url || 'https://ctroads.org'}" target="_blank" rel="noopener">${cam.source || 'CT DOT'}</a></p>
                <p class="cam-modal-note">Camera refreshes automatically. No recordings available.</p>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Setup close button
    const closeBtn = modal.querySelector('.cam-close');
    closeBtn.onclick = () => closeCamModal(modal);
    
    // Close on backdrop click
    modal.onclick = (e) => {
        if (e.target === modal) {
            closeCamModal(modal);
        }
    };

    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            closeCamModal(modal);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);

    // Focus management
    closeBtn.focus();

    // Setup refresh for modal image
    const modalImg = document.getElementById(`cam-modal-img-${cam.id}`);
    if (modalImg && cam.refresh_ms && cam.refresh_ms > 0) {
        const modalIntervalId = setInterval(() => {
            if (modalImg && document.body.contains(modal)) {
                const separator = cam.feed_url.includes('?') ? '&' : '?';
                modalImg.src = `${cam.feed_url}${separator}ts=${Date.now()}`;
            } else {
                clearInterval(modalIntervalId);
            }
        }, cam.refresh_ms);
        
        // Store interval ID so we can clear it when modal closes
        modal.dataset.intervalId = modalIntervalId;
    }
}

/**
 * Close camera modal
 */
function closeCamModal(modal) {
    // Clear refresh interval if set
    if (modal.dataset.intervalId) {
        clearInterval(parseInt(modal.dataset.intervalId));
    }
    modal.remove();
}

/**
 * Cleanup refresh intervals
 */
function cleanup() {
    Object.values(refreshIntervals).forEach(intervalId => {
        clearInterval(intervalId);
    });
    refreshIntervals = {};
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', async () => {
    await fetchCameras();
    buildCamGallery('traffic-cam-gallery');
});

// Cleanup on page unload
window.addEventListener('beforeunload', cleanup);

