// Confirmation prompt for deleting data
function confirmDelete() {
    return confirm('Are you sure you want to delete this entry? This action cannot be undone.');
}

// Auto-close flash messages after 3 seconds
window.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.display = 'none';
        }, 3000);
    });
});

// Highlight invalid fields
function validateForm() {
    const inputs = document.querySelectorAll('input[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.border = '2px solid #a94442';
            isValid = false;
        } else {
            input.style.border = '2px solid #4CAF50';
        }
    });

    return isValid;
}
