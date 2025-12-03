/**
 * Live CAM 78 - Real-time video simulation from CTDOT JPEG feed
 * Simulates 24fps video by rapidly refreshing JPEG frames
 */

(function() {
    'use strict';

    const canvas = document.getElementById("cam78Canvas");
    if (!canvas) {
        console.warn("CAM 78 canvas not found");
        return;
    }

    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";

    const FRAME_RATE = 24;
    const FRAME_INTERVAL = 1000 / FRAME_RATE; // ~41.67ms

    const CAM_ID = "590";
    const BASE_URL = "https://ctroads.org/cctv";
    
    const FRAME_URL = () => `${BASE_URL}/${CAM_ID}.jpg?rnd=${Date.now()}`;

    let isRunning = true;
    let lastFrameTime = 0;
    let frameLoadStart = 0;
    let errorCount = 0;
    const MAX_ERRORS = 5;

    /**
     * Fetch a single frame as an Image object
     */
    async function fetchFrame() {
        return new Promise((resolve, reject) => {
            const img = new Image();
            
            // Handle CORS - try anonymous first
            img.crossOrigin = "Anonymous";
            
            img.onload = () => {
                errorCount = 0; // Reset error count on success
                resolve(img);
            };
            
            img.onerror = (err) => {
                errorCount++;
                if (errorCount >= MAX_ERRORS) {
                    console.error("CAM 78: Too many consecutive errors, pausing");
                    isRunning = false;
                }
                reject(err);
            };
            
            // Add timestamp to bypass cache
            img.src = FRAME_URL();
        });
    }

    /**
     * Render a frame to the canvas
     */
    function renderFrame(img) {
        try {
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw image, scaling to fit canvas dimensions
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            
            lastFrameTime = performance.now();
        } catch (err) {
            console.warn("CAM 78: Render error:", err);
        }
    }

    /**
     * Main render loop - fetches and renders frames at 24fps
     */
    async function renderLoop() {
        if (!isRunning) {
            return;
        }

        const now = performance.now();
        const timeSinceLastFrame = now - lastFrameTime;
        
        // If we're ahead of schedule, wait a bit
        if (timeSinceLastFrame < FRAME_INTERVAL - 5) {
            setTimeout(renderLoop, FRAME_INTERVAL - timeSinceLastFrame);
            return;
        }

        frameLoadStart = now;

        try {
            const img = await fetchFrame();
            
            // Only render if we're still running (user might have navigated away)
            if (isRunning && canvas && ctx) {
                renderFrame(img);
            }
        } catch (err) {
            // Error already logged in fetchFrame
            // Continue loop even on error to retry
        }

        // Schedule next frame
        const elapsed = performance.now() - frameLoadStart;
        const delay = Math.max(0, FRAME_INTERVAL - elapsed);
        
        if (isRunning) {
            setTimeout(renderLoop, delay);
        }
    }

    /**
     * Initialize when DOM is ready
     */
    function init() {
        if (!canvas || !ctx) {
            console.error("CAM 78: Canvas or context not available");
            return;
        }

        // Set canvas dimensions if not already set
        // Check if canvas already has dimensions set in HTML
        if (canvas.width === 0 || canvas.height === 0) {
            // Default to square for widget, but check if we're in full-width mode
            const isFullWidth = document.getElementById('liveCam78');
            if (isFullWidth) {
                canvas.width = 640;
                canvas.height = 360;
            } else {
                // Square widget mode
                const container = canvas.closest('.live-cam-widget__container');
                if (container) {
                    const size = container.offsetWidth;
                    canvas.width = size;
                    canvas.height = size;
                } else {
                    canvas.width = 360;
                    canvas.height = 360;
                }
            }
        }

        // Draw initial placeholder
        ctx.fillStyle = "#1a1a1a";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#666";
        ctx.font = "16px Inter, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("Loading CAM 78...", canvas.width / 2, canvas.height / 2);

        // Start render loop
        lastFrameTime = performance.now();
        renderLoop();
    }

    // Start when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // Cleanup on page unload
    window.addEventListener("beforeunload", () => {
        isRunning = false;
    });

    // Expose cleanup function for manual control if needed
    window.cam78Stop = () => {
        isRunning = false;
    };

    window.cam78Start = () => {
        if (!isRunning) {
            isRunning = true;
            errorCount = 0;
            renderLoop();
        }
    };
})();

