/**
 * Business Hours Management JavaScript
 * Additional client-side functionality for business hours pages
 */

// Utility function to format time for display
function formatTimeForDisplay(time24) {
    if (!time24) return '';
    
    const [hours, minutes] = time24.split(':');
    const hour = parseInt(hours, 10);
    const period = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
    
    return `${hour12}:${minutes} ${period}`;
}

// Utility function to check if business is currently open
function isBusinessOpenNow(business) {
    if (!business.hours || business.hours.length === 0) {
        return null; // Unknown
    }
    
    const now = new Date();
    const currentDay = now.toLocaleDateString('en-US', { weekday: 'long' });
    const currentTime = now.toTimeString().slice(0, 5); // HH:MM format
    
    const todayHours = business.hours.find(h => h.day === currentDay);
    if (!todayHours || todayHours.is_closed) {
        return false;
    }
    
    if (!todayHours.open_time || !todayHours.close_time) {
        return null; // Unknown
    }
    
    return currentTime >= todayHours.open_time && currentTime <= todayHours.close_time;
}

// Add "Open Now" indicator to business cards
document.addEventListener('DOMContentLoaded', function() {
    const businessCards = document.querySelectorAll('.business-card');
    
    businessCards.forEach(card => {
        // This would require fetching business data via API
        // For now, this is a placeholder for future enhancement
    });
});

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatTimeForDisplay,
        isBusinessOpenNow
    };
}





