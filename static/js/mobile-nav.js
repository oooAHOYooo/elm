/**
 * Mobile Navigation System for Elm City Daily
 * Bottom navigation bar with tab-based content switching
 * No scrolling - everything fits on screen
 */

(function() {
    'use strict';

    const MOBILE_BREAKPOINT = 768;
    let currentTab = 'home';
    let isMobile = false;

    // Tab definitions with icons and content selectors
    const tabs = [
        {
            id: 'home',
            label: 'Home',
            icon: '🏠',
            contentSelector: '.mobile-tab-home',
            default: true
        },
        {
            id: 'events',
            label: 'Events',
            icon: '📅',
            contentSelector: '.mobile-tab-events'
        },
        {
            id: 'news',
            label: 'News',
            icon: '📰',
            contentSelector: '.mobile-tab-news'
        },
        {
            id: 'civics',
            label: 'Civics',
            icon: '🏛️',
            contentSelector: '.mobile-tab-civics'
        },
        {
            id: 'change',
            label: 'Change',
            icon: '🔧',
            contentSelector: '.mobile-tab-change'
        },
        {
            id: 'cams',
            label: 'Cams',
            icon: '📹',
            contentSelector: '.mobile-tab-cams'
        },
        {
            id: 'weather',
            label: 'Weather',
            icon: '🌤️',
            contentSelector: '.mobile-tab-weather'
        }
    ];

    /**
     * Check if we're on mobile
     */
    function checkMobile() {
        const wasMobile = isMobile;
        isMobile = window.innerWidth <= MOBILE_BREAKPOINT;
        
        if (wasMobile !== isMobile) {
            initMobileNav();
        }
        
        return isMobile;
    }

    /**
     * Create bottom navigation bar
     */
    function createBottomNav() {
        // Remove existing nav if present
        const existingNav = document.getElementById('mobile-bottom-nav');
        if (existingNav) {
            existingNav.remove();
        }

        const nav = document.createElement('nav');
        nav.id = 'mobile-bottom-nav';
        nav.className = 'mobile-bottom-nav';
        nav.setAttribute('role', 'navigation');
        nav.setAttribute('aria-label', 'Main navigation');

        tabs.forEach(tab => {
            const button = document.createElement('button');
            button.className = 'mobile-nav-item';
            button.setAttribute('data-tab', tab.id);
            button.setAttribute('aria-label', tab.label);
            button.setAttribute('role', 'tab');
            button.setAttribute('aria-selected', tab.id === currentTab ? 'true' : 'false');
            
            button.innerHTML = `
                <span class="mobile-nav-icon">${tab.icon}</span>
                <span class="mobile-nav-label">${tab.label}</span>
            `;
            
            button.addEventListener('click', () => switchTab(tab.id));
            nav.appendChild(button);
        });

        document.body.appendChild(nav);
    }

    /**
     * Switch to a different tab
     */
    function switchTab(tabId) {
        if (currentTab === tabId) return;

        // Update current tab
        currentTab = tabId;

        // Hide all tab content
        document.querySelectorAll('.mobile-tab-content').forEach(content => {
            content.classList.remove('active');
            content.setAttribute('aria-hidden', 'true');
        });

        // Show selected tab content
        const tab = tabs.find(t => t.id === tabId);
        if (tab) {
            const content = document.querySelector(tab.contentSelector);
            if (content) {
                content.classList.add('active');
                content.setAttribute('aria-hidden', 'false');
            }
        }

        // Update nav buttons
        document.querySelectorAll('.mobile-nav-item').forEach(btn => {
            const isActive = btn.getAttribute('data-tab') === tabId;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });

        // Scroll to top of content
        const dashboard = document.getElementById('js-fit');
        if (dashboard) {
            dashboard.scrollTop = 0;
        }

        // Trigger resize for any components that need it
        window.dispatchEvent(new Event('resize'));
    }

    /**
     * Organize content into mobile tabs
     */
    function organizeMobileContent() {
        const dashboard = document.getElementById('js-fit');
        if (!dashboard) return;

        // Create mobile tab containers
        const tabContainer = document.createElement('div');
        tabContainer.className = 'mobile-tabs-container';
        tabContainer.id = 'mobile-tabs-container';

        // Home tab - main dashboard content
        const homeTab = document.createElement('div');
        homeTab.className = 'mobile-tab-content mobile-tab-home active';
        homeTab.setAttribute('aria-hidden', 'false');
        homeTab.setAttribute('role', 'tabpanel');
        homeTab.setAttribute('aria-labelledby', 'tab-home');

        // Events tab - week events and agenda
        const eventsTab = document.createElement('div');
        eventsTab.className = 'mobile-tab-content mobile-tab-events';
        eventsTab.setAttribute('aria-hidden', 'true');
        eventsTab.setAttribute('role', 'tabpanel');
        eventsTab.setAttribute('aria-labelledby', 'tab-events');

        // News tab - news items
        const newsTab = document.createElement('div');
        newsTab.className = 'mobile-tab-content mobile-tab-news';
        newsTab.setAttribute('aria-hidden', 'true');
        newsTab.setAttribute('role', 'tabpanel');
        newsTab.setAttribute('aria-labelledby', 'tab-news');

        // Civics tab - council actions and stats
        const civicsTab = document.createElement('div');
        civicsTab.className = 'mobile-tab-content mobile-tab-civics';
        civicsTab.setAttribute('aria-hidden', 'true');
        civicsTab.setAttribute('role', 'tabpanel');
        civicsTab.setAttribute('aria-labelledby', 'tab-civics');

        // Change New Haven tab - all Change New Haven links
        const changeTab = document.createElement('div');
        changeTab.className = 'mobile-tab-content mobile-tab-change';
        changeTab.setAttribute('aria-hidden', 'true');
        changeTab.setAttribute('role', 'tabpanel');
        changeTab.setAttribute('aria-labelledby', 'tab-change');

        // Cams tab - traffic cameras
        const camsTab = document.createElement('div');
        camsTab.className = 'mobile-tab-content mobile-tab-cams';
        camsTab.setAttribute('aria-hidden', 'true');
        camsTab.setAttribute('role', 'tabpanel');
        camsTab.setAttribute('aria-labelledby', 'tab-cams');

        // Weather tab - weather and alerts
        const weatherTab = document.createElement('div');
        weatherTab.className = 'mobile-tab-content mobile-tab-weather';
        weatherTab.setAttribute('aria-hidden', 'true');
        weatherTab.setAttribute('role', 'tabpanel');
        weatherTab.setAttribute('aria-labelledby', 'tab-weather');

        // Find and move content to appropriate tabs
        const main = dashboard.querySelector('main.grid');
        const strip = dashboard.querySelector('section.strip');
        const liveCam = dashboard.querySelector('#liveCam78');
        const footer = dashboard.querySelector('footer.footer-mini');

        if (main) {
            // Extract panels
            const leftPanel = main.querySelector('.panel--left');
            const centerPanel = main.querySelector('.panel--center');
            const rightPanel = main.querySelector('.panel--right');

            // Home: Compact view with key info
            if (centerPanel) {
                const centerClone = centerPanel.cloneNode(true);
                homeTab.appendChild(centerClone);
            }

            // Events: Week agenda and events
            if (centerPanel) {
                const agendaSection = centerPanel.querySelector('.agenda--vertical');
                const eventsList = rightPanel?.querySelector('.list--rail');
                if (agendaSection) {
                    const agendaClone = agendaSection.cloneNode(true);
                    eventsTab.appendChild(agendaClone);
                }
                if (eventsList) {
                    const eventsClone = eventsList.cloneNode(true);
                    eventsTab.appendChild(eventsClone);
                }
            }

            // News: News items from right panel
            if (rightPanel) {
                const newsItems = rightPanel.querySelectorAll('.list--rail .list__item');
                if (newsItems.length > 0) {
                    const newsList = document.createElement('ul');
                    newsList.className = 'list';
                    newsItems.forEach(item => newsList.appendChild(item.cloneNode(true)));
                    newsTab.appendChild(newsList);
                }
            }

            // Civics: Stats and council actions
            if (leftPanel) {
                const stats = leftPanel.querySelector('.stats');
                const civicsList = leftPanel.querySelector('.list--supporting');
                if (stats) {
                    const statsClone = stats.cloneNode(true);
                    civicsTab.appendChild(statsClone);
                }
                if (civicsList) {
                    const civicsClone = civicsList.cloneNode(true);
                    civicsTab.appendChild(civicsClone);
                }
            }

            // Change New Haven: All Change New Haven links
            if (leftPanel) {
                const changeNH = leftPanel.querySelector('.change-nh');
                if (changeNH) {
                    const changeClone = changeNH.cloneNode(true);
                    changeTab.appendChild(changeClone);
                }
            }

            // Cams: Live camera
            if (liveCam) {
                const camClone = liveCam.cloneNode(true);
                camsTab.appendChild(camClone);
            }

            // Weather: Weather info from right panel
            if (rightPanel) {
                const weatherSection = rightPanel.querySelector('.weather');
                const nwsAlerts = rightPanel.querySelector('.alerts');
                if (weatherSection) {
                    const weatherClone = weatherSection.cloneNode(true);
                    weatherTab.appendChild(weatherClone);
                }
                if (nwsAlerts) {
                    const alertsClone = nwsAlerts.cloneNode(true);
                    weatherTab.appendChild(alertsClone);
                }
            }
        }

        // Append tabs to container
        tabContainer.appendChild(homeTab);
        tabContainer.appendChild(eventsTab);
        tabContainer.appendChild(newsTab);
        tabContainer.appendChild(civicsTab);
        tabContainer.appendChild(changeTab);
        tabContainer.appendChild(camsTab);
        tabContainer.appendChild(weatherTab);

        // Insert before footer
        if (footer) {
            footer.parentNode.insertBefore(tabContainer, footer);
        } else {
            dashboard.appendChild(tabContainer);
        }

        // Hide original content on mobile
        if (main) main.style.display = 'none';
        if (strip) strip.style.display = 'none';
        if (liveCam) liveCam.style.display = 'none';
    }

    /**
     * Restore desktop layout
     */
    function restoreDesktopLayout() {
        const tabContainer = document.getElementById('mobile-tabs-container');
        const bottomNav = document.getElementById('mobile-bottom-nav');
        const main = document.querySelector('main.grid');
        const strip = document.querySelector('section.strip');
        const liveCam = document.querySelector('#liveCam78');

        if (tabContainer) tabContainer.remove();
        if (bottomNav) bottomNav.remove();
        if (main) main.style.display = '';
        if (strip) strip.style.display = '';
        if (liveCam) liveCam.style.display = '';
    }

    /**
     * Initialize mobile navigation
     */
    function initMobileNav() {
        if (isMobile) {
            organizeMobileContent();
            createBottomNav();
            // Set default tab
            const defaultTab = tabs.find(t => t.default) || tabs[0];
            switchTab(defaultTab.id);
        } else {
            restoreDesktopLayout();
        }
    }

    /**
     * Initialize on DOM ready
     */
    function init() {
        checkMobile();
        initMobileNav();

        // Watch for resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                checkMobile();
            }, 150);
        });

        // Handle orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                checkMobile();
            }, 300);
        });
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export for external use
    window.mobileNav = {
        switchTab,
        getCurrentTab: () => currentTab,
        isMobile: () => isMobile
    };
})();

