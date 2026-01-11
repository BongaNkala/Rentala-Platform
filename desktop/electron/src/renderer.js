// Desktop App Renderer Process

class RentalaDesktop {
    constructor() {
        this.init();
    }
    
    async init() {
        // Check if user is logged in
        const token = await window.electronAPI.store.get('auth_token');
        
        if (token) {
            this.setupAuthenticatedApp(token);
        } else {
            this.setupLoginScreen();
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Check for updates
        this.checkForUpdates();
    }
    
    setupAuthenticatedApp(token) {
        // Decode JWT to get user info
        const payload = JSON.parse(atob(token.split('.')[1]));
        this.user = payload;
        
        // Update UI with user info
        document.getElementById('user-avatar').src = this.user.avatar || 'default-avatar.png';
        document.getElementById('user-name').textContent = this.user.first_name;
        
        // Load user data
        this.loadUserData();
        
        // Setup WebSocket connection for real-time updates
        this.setupWebSocket();
    }
    
    setupLoginScreen() {
        // Show login form
        document.getElementById('login-screen').classList.remove('d-none');
        document.getElementById('main-app').classList.add('d-none');
        
        // Setup login form handler
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const remember = document.getElementById('remember').checked;
            
            try {
                const response = await window.electronAPI.api.request({
                    method: 'POST',
                    url: '/token/',
                    data: { email, password }
                });
                
                if (response.data.access) {
                    // Store token
                    await window.electronAPI.store.set('auth_token', response.data.access);
                    
                    // Store refresh token if remember me is checked
                    if (remember) {
                        await window.electronAPI.store.set('refresh_token', response.data.refresh);
                    }
                    
                    // Store user info
                    await window.electronAPI.store.set('user', response.data.user);
                    
                    // Reload app
                    location.reload();
                }
            } catch (error) {
                this.showError('Login failed: ' + error);
            }
        });
    }
    
    async loadUserData() {
        try {
            // Load user profile
            const profile = await window.electronAPI.api.request({
                method: 'GET',
                url: `/users/${this.user.user_id}/`
            });
            
            // Load bookings
            const bookings = await window.electronAPI.api.request({
                method: 'GET',
                url: '/bookings/'
            });
            
            // Load listings if host
            if (this.user.is_host) {
                const listings = await window.electronAPI.api.request({
                    method: 'GET',
                    url: '/listings/',
                    params: { host: this.user.user_id }
                });
                this.renderListings(listings.data);
            }
            
            this.renderBookings(bookings.data);
            this.renderProfile(profile.data);
            
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }
    
    setupWebSocket() {
        // WebSocket connection for real-time updates
        this.ws = new WebSocket('ws://localhost:8000/ws/');
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            // Send authentication
            this.ws.send(JSON.stringify({
                type: 'auth',
                token: await window.electronAPI.store.get('auth_token')
            }));
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting...');
            setTimeout(() => this.setupWebSocket(), 5000);
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'notification':
                this.showNotification(data.title, data.message);
                break;
            case 'booking_update':
                this.updateBooking(data.booking);
                break;
            case 'new_message':
                this.showNewMessage(data.message);
                break;
        }
    }
    
    setupEventListeners() {
        // Logout button
        document.getElementById('logout-btn').addEventListener('click', async () => {
            await window.electronAPI.store.delete('auth_token');
            await window.electronAPI.store.delete('refresh_token');
            location.reload();
        });
        
        // New booking button
        document.getElementById('new-booking-btn').addEventListener('click', () => {
            this.openBookingModal();
        });
        
        // Sync button
        document.getElementById('sync-btn').addEventListener('click', () => {
            this.syncData();
        });
        
        // Electron events
        window.electronAPI.on('new-booking', () => {
            this.openBookingModal();
        });
        
        window.electronAPI.on('open-preferences', () => {
            this.openPreferences();
        });
        
        window.electronAPI.on('update-available', () => {
            this.showUpdateAvailable();
        });
        
        window.electronAPI.on('update-downloaded', () => {
            this.showUpdateDownloaded();
        });
    }
    
    async syncData() {
        // Show sync indicator
        document.getElementById('sync-btn').disabled = true;
        document.getElementById('sync-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Syncing...';
        
        try {
            // Sync offline data
            const offlineData = await window.electronAPI.store.get('offline_data');
            if (offlineData && offlineData.length > 0) {
                for (const item of offlineData) {
                    await window.electronAPI.api.request({
                        method: item.method,
                        url: item.url,
                        data: item.data
                    });
                }
                // Clear offline data
                await window.electronAPI.store.delete('offline_data');
            }
            
            // Refresh local data
            await this.loadUserData();
            
            this.showSuccess('Data synced successfully');
        } catch (error) {
            this.showError('Sync failed: ' + error);
        } finally {
            // Reset sync button
            document.getElementById('sync-btn').disabled = false;
            document.getElementById('sync-btn').innerHTML = '<i class="fas fa-sync"></i> Sync';
        }
    }
    
    showNotification(title, message) {
        window.electronAPI.notifications.show(title, message);
        
        // Also show in-app notification
        const notification = document.createElement('div');
        notification.className = 'notification alert alert-info';
        notification.innerHTML = `
            <strong>${title}</strong>
            <p>${message}</p>
            <button class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.getElementById('notifications').appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    showError(message) {
        const error = document.createElement('div');
        error.className = 'notification alert alert-danger';
        error.innerHTML = `
            <strong>Error</strong>
            <p>${message}</p>
            <button class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.getElementById('notifications').appendChild(error);
    }
    
    showSuccess(message) {
        const success = document.createElement('div');
        success.className = 'notification alert alert-success';
        success.innerHTML = `
            <strong>Success</strong>
            <p>${message}</p>
            <button class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.getElementById('notifications').appendChild(success);
    }
    
    checkForUpdates() {
        // Auto updater is handled by main process
        // This just shows status
        setInterval(async () => {
            try {
                const response = await window.electronAPI.api.request({
                    method: 'GET',
                    url: '/version/'
                });
                
                const currentVersion = '1.0.0'; // Should be from package.json
                if (response.data.version !== currentVersion) {
                    this.showUpdateAvailable();
                }
            } catch (error) {
                // Silent fail
            }
        }, 3600000); // Check every hour
    }
    
    showUpdateAvailable() {
        if (confirm('A new version is available. Would you like to update now?')) {
            // Trigger update
            // This would normally be handled by autoUpdater
            this.showNotification('Update', 'Downloading update...');
        }
    }
    
    showUpdateDownloaded() {
        if (confirm('Update downloaded. Restart now to install?')) {
            // Restart app
            window.electronAPI.api.request({
                method: 'POST',
                url: '/restart/'
            });
        }
    }
    
    openBookingModal() {
        // Implement booking modal
        console.log('Open booking modal');
    }
    
    openPreferences() {
        // Implement preferences modal
        console.log('Open preferences');
    }
    
    renderBookings(bookings) {
        const container = document.getElementById('bookings-list');
        container.innerHTML = '';
        
        bookings.forEach(booking => {
            const bookingElement = document.createElement('div');
            bookingElement.className = 'booking-card card mb-3';
            bookingElement.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${booking.listing.title}</h5>
                    <p class="card-text">
                        <i class="fas fa-calendar"></i> ${booking.check_in} - ${booking.check_out}<br>
                        <i class="fas fa-users"></i> ${booking.number_of_guests} guests<br>
                        <span class="badge bg-${this.getStatusColor(booking.status)}">${booking.status}</span>
                    </p>
                    <div class="d-flex justify-content-between">
                        <span class="fw-bold">$${booking.total_price}</span>
                        <button class="btn btn-sm btn-outline-primary view-booking" data-id="${booking.id}">View</button>
                    </div>
                </div>
            `;
            
            container.appendChild(bookingElement);
        });
        
        // Add event listeners to view buttons
        document.querySelectorAll('.view-booking').forEach(button => {
            button.addEventListener('click', (e) => {
                const bookingId = e.target.dataset.id;
                this.viewBooking(bookingId);
            });
        });
    }
    
    renderListings(listings) {
        const container = document.getElementById('listings-list');
        container.innerHTML = '';
        
        listings.forEach(listing => {
            const listingElement = document.createElement('div');
            listingElement.className = 'listing-card card mb-3';
            listingElement.innerHTML = `
                <img src="${listing.primary_image || 'default.jpg'}" class="card-img-top" alt="${listing.title}">
                <div class="card-body">
                    <h5 class="card-title">${listing.title}</h5>
                    <p class="card-text">
                        <i class="fas fa-map-marker-alt"></i> ${listing.city}, ${listing.country}<br>
                        <i class="fas fa-dollar-sign"></i> $${listing.price_per_day}/night
                    </p>
                    <div class="d-flex justify-content-between">
                        <span class="badge bg-${listing.status === 'active' ? 'success' : 'warning'}">${listing.status}</span>
                        <button class="btn btn-sm btn-outline-primary edit-listing" data-id="${listing.id}">Edit</button>
                    </div>
                </div>
            `;
            
            container.appendChild(listingElement);
        });
    }
    
    renderProfile(profile) {
        document.getElementById('profile-name').textContent = `${profile.first_name} ${profile.last_name}`;
        document.getElementById('profile-email').textContent = profile.email;
        document.getElementById('profile-phone').textContent = profile.phone || 'Not set';
        
        if (profile.is_host) {
            document.getElementById('host-stats').classList.remove('d-none');
            // Populate host stats
        }
    }
    
    getStatusColor(status) {
        const colors = {
            'confirmed': 'success',
            'pending': 'warning',
            'cancelled': 'danger',
            'completed': 'info'
        };
        return colors[status] || 'secondary';
    }
    
    viewBooking(bookingId) {
        // Implement booking detail view
        console.log('View booking:', bookingId);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.rentalaDesktop = new RentalaDesktop();
});
