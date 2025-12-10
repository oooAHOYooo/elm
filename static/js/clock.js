(function() {
    'use strict';

    const STORAGE_KEY = 'clockFormatId';

    const weekdayShort = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const monthShort = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    function pad2(n) {
        return String(n).padStart(2, '0');
    }

    function formatISO(dt) {
        const y = dt.getFullYear();
        const m = pad2(dt.getMonth() + 1);
        const d = pad2(dt.getDate());
        const hh = pad2(dt.getHours());
        const mm = pad2(dt.getMinutes());
        const ss = pad2(dt.getSeconds());
        return `${y}-${m}-${d} ${hh}:${mm}:${ss}`;
    }

    const FORMATS = [
        {
            id: 'time-24',
            label: '24h',
            format: (dt) => `${pad2(dt.getHours())}:${pad2(dt.getMinutes())}:${pad2(dt.getSeconds())}`
        },
        {
            id: 'time-12',
            label: '12h',
            format: (dt) => {
                const h24 = dt.getHours();
                const h12 = h24 % 12 === 0 ? 12 : h24 % 12;
                const ampm = h24 < 12 ? 'AM' : 'PM';
                return `${h12}:${pad2(dt.getMinutes())}:${pad2(dt.getSeconds())} ${ampm}`;
            }
        },
        {
            id: 'iso',
            label: 'ISO',
            format: (dt) => formatISO(dt)
        },
        {
            id: 'weekday',
            label: 'Weekday',
            format: (dt) => {
                const w = weekdayShort[dt.getDay()];
                const m = monthShort[dt.getMonth()];
                const d = pad2(dt.getDate());
                const hh = pad2(dt.getHours());
                const mm = pad2(dt.getMinutes());
                const ss = pad2(dt.getSeconds());
                return `${w}, ${m} ${d} ${hh}:${mm}:${ss}`;
            }
        },
        {
            id: 'utc',
            label: 'UTC',
            format: (dt) => dt.toUTCString().replace(' GMT', '')
        }
    ];

    function getInitialFormatId() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved && FORMATS.some(f => f.id === saved)) {
                return saved;
            }
        } catch {}
        return FORMATS[0].id;
    }

    function startClock(el) {
        let currentFormatId = getInitialFormatId();

        function render() {
            const now = new Date();
            const fmt = FORMATS.find(f => f.id === currentFormatId) || FORMATS[0];
            el.textContent = fmt.format(now);
            el.setAttribute('aria-label', `Clock (${fmt.label}). Click to change format.`);
            el.setAttribute('title', `Format: ${fmt.label} — click to change`);
        }

        function cycleFormat() {
            const idx = FORMATS.findIndex(f => f.id === currentFormatId);
            const nextIdx = (idx + 1) % FORMATS.length;
            currentFormatId = FORMATS[nextIdx].id;
            try {
                localStorage.setItem(STORAGE_KEY, currentFormatId);
            } catch {}
            render();
        }

        el.addEventListener('click', cycleFormat);

        // Align first tick to the next second boundary
        const now = Date.now();
        const msToNextSecond = 1000 - (now % 1000);
        render();
        setTimeout(() => {
            render();
            setInterval(render, 1000);
        }, msToNextSecond);
    }

    function init() {
        const el = document.getElementById('digital-clock');
        if (!el) return;
        startClock(el);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();



