// Maroof Cards - Main JavaScript

// Show alert message
function showAlert(message, type) {
    const alert = document.getElementById('alert');
    if (!alert) return;
    
    alert.textContent = message;
    alert.className = `alert alert-${type} show`;
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

// Update pending count badge
async function updatePendingCount() {
    try {
        const response = await fetch('/api/pending-count');
        const data = await response.json();
        const badge = document.getElementById('pendingBadge');
        if (badge) {
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Failed to update pending count');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Update pending count on all pages
    if (document.getElementById('pendingBadge')) {
        updatePendingCount();
        setInterval(updatePendingCount, 10000);
    }
});
