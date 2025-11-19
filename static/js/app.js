// Echo Language - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();

    // Auto-hide flash messages
    autoHideFlashMessages();
});

function initTooltips() {
    // Simple tooltip initialization if needed
}

function autoHideFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });
}

// Utility function for API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(endpoint, options);
    return response.json();
}

// Practice button functionality
async function quickPractice() {
    const result = await apiCall('/api/practice', 'POST');
    if (result.streak) {
        // Update UI with new streak
        const streakDisplay = document.querySelector('.stat-item.streak');
        if (streakDisplay) {
            streakDisplay.textContent = `${result.streak} days`;
        }
    }
}
