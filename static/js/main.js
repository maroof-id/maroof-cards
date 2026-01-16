// Maroof Cards - Main JavaScript

// Show alert message
function showAlert(message, type) {
    const alert = document.getElementById('alert');
    if (!alert) return;
    
    alert.textContent = message;
    alert.className = `alert alert-${type} show`;
    
    // Scroll to alert
    alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
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

// Handle photo preview
function handlePhotoPreview(e) {
    const file = e.target.files[0];
    if (file) {
        if (file.size > 5 * 1024 * 1024) {
            showAlert('الصورة كبيرة جداً! الحد الأقصى 5MB', 'error');
            e.target.value = '';
            document.getElementById('photoPreview').style.display = 'none';
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(event) {
            document.getElementById('previewImage').src = event.target.result;
            document.getElementById('photoPreview').style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        document.getElementById('photoPreview').style.display = 'none';
    }
}

// Convert file to Base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Update pending count on all pages
    if (document.getElementById('pendingBadge')) {
        updatePendingCount();
        setInterval(updatePendingCount, 10000);
    }
});