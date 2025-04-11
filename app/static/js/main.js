/**
 * Main JavaScript file for Planora Scheduler Application
 */

// Flash message handling
document.addEventListener('DOMContentLoaded', function() {
    // Handle flash messages (if any)
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'flash-close';
        message.appendChild(closeBtn);
        
        // Handle close click
        closeBtn.addEventListener('click', function() {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        });
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Form validation - add required attribute to all inputs in form groups
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const label = group.querySelector('label');
        if (label && label.textContent.indexOf('optional') === -1) {
            const input = group.querySelector('input');
            if (input) {
                input.setAttribute('required', 'required');
            }
        }
    });
});