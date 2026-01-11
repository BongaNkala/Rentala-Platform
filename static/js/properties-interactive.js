// Properties Page Interactive Enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Property card hover effects
    const propertyCards = document.querySelectorAll('.property-card');
    
    propertyCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.zIndex = '1';
        });
    });

    // Status badge animations
    const statusBadges = document.querySelectorAll('.property-status');
    
    statusBadges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Feature icons pulse animation
    const featureIcons = document.querySelectorAll('.property-feature i');
    
    featureIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.animation = 'pulse 0.5s ease';
        });
        
        icon.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const propertyCards = document.querySelectorAll('.property-card');
            
            propertyCards.forEach(card => {
                const title = card.querySelector('.property-card-title span:first-child').textContent.toLowerCase();
                const location = card.querySelector('.property-location span').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || location.includes(searchTerm)) {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.5s ease';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Add property form submission
    const addPropertyForm = document.querySelector('.property-form-container');
    if (addPropertyForm) {
        const saveButton = addPropertyForm.querySelector('.btn-primary');
        
        saveButton.addEventListener('click', function() {
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            this.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-check"></i> Saved!';
                this.classList.add('btn-success');
                this.classList.remove('btn-primary');
                
                // Reset form
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-save"></i> Save Property';
                    this.disabled = false;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-primary');
                    
                    // Show success notification
                    showNotification('Property added successfully!', 'success');
                }, 1500);
            }, 2000);
        });
    }

    // Action buttons functionality
    const viewButtons = document.querySelectorAll('.btn-view');
    const editButtons = document.querySelectorAll('.btn-edit');
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const propertyCard = this.closest('.property-card');
            const propertyName = propertyCard.querySelector('.property-card-title span:first-child').textContent;
            showNotification(`Viewing ${propertyName} details`, 'info');
        });
    });
    
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const propertyCard = this.closest('.property-card');
            const propertyName = propertyCard.querySelector('.property-card-title span:first-child').textContent;
            showNotification(`Editing ${propertyName}`, 'warning');
        });
    });

    // Notification system
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${getIconForType(type)}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) reverse';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    function getIconForType(type) {
        switch(type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-circle';
            case 'warning': return 'exclamation-triangle';
            case 'info': return 'info-circle';
            default: return 'bell';
        }
    }

    // Initialize property stats with counting animation
    const statValues = document.querySelectorAll('.property-stat-value');
    
    statValues.forEach(statValue => {
        const finalValue = statValue.textContent;
        if (!isNaN(parseFloat(finalValue))) {
            animateCount(statValue, parseFloat(finalValue));
        }
    });
    
    function animateCount(element, finalValue) {
        let startValue = 0;
        const duration = 1500;
        const startTime = Date.now();
        
        function updateCount() {
            const currentTime = Date.now();
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            
            const currentValue = startValue + (finalValue - startValue) * easeOutQuart;
            
            if (element.textContent.includes('R') || element.textContent.includes('%')) {
                const prefix = element.textContent.includes('R') ? 'R' : '';
                const suffix = element.textContent.includes('%') ? '%' : '';
                element.textContent = `${prefix}${Math.round(currentValue)}${suffix}`;
            } else {
                element.textContent = Math.round(currentValue);
            }
            
            if (progress < 1) {
                requestAnimationFrame(updateCount);
            }
        }
        
        updateCount();
    }
});

// Add CSS for notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification {
        position: fixed;
        top: 30px;
        right: 30px;
        padding: 18px 24px;
        border-radius: 16px;
        color: white;
        font-weight: 600;
        z-index: 2000;
        max-width: 400px;
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-success {
        background: rgba(74, 222, 128, 0.2);
        border-color: rgba(74, 222, 128, 0.3);
        color: #4ade80;
    }
    
    .notification-error {
        background: rgba(239, 68, 68, 0.2);
        border-color: rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }
    
    .notification-warning {
        background: rgba(245, 158, 11, 0.2);
        border-color: rgba(245, 158, 11, 0.3);
        color: #f59e0b;
    }
    
    .notification-info {
        background: rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
        color: #3b82f6;
    }
    
    .notification i {
        font-size: 20px;
    }
`;
document.head.appendChild(notificationStyles);
