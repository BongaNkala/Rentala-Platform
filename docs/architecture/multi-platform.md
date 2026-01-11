# Rentala Multi-Platform Architecture

## Overview
Rentala supports three main platforms:
1. **Customer Portal (Web)** - Primary web interface
2. **Desktop Application** - Native desktop experience
3. **Mobile Applications** - iOS & Android (future)

## Core Components

### 1. Backend API (Django REST Framework)
- Single source of truth
- RESTful endpoints for all platforms
- WebSocket support for real-time features
- Platform-agnostic data models

### 2. Customer Portal (Web)
- Django Templates + Bootstrap
- Progressive Web App (PWA) capabilities
- Service workers for offline functionality
- Responsive design

### 3. Desktop Application
- **Option 1:** Electron (HTML/CSS/JS)
- **Option 2:** PyQt (Python)
- **Option 3:** Tauri (Rust + Web)
- **Features:**
  - System tray integration
  - Offline mode
  - Desktop notifications
  - File system access
  - Auto-updates

### 4. Mobile Applications (Future)
- React Native or Flutter
- Push notifications
- Camera/photo integration
- Location services
- Offline storage

## Data Flow
1. All platforms → REST API
2. Real-time updates → WebSocket/Server-Sent Events
3. Offline data → Local storage sync
4. File uploads → CDN with platform optimizations

## Authentication Flow
1. JWT tokens for API access
2. Platform-specific session management
3. OAuth2 for social logins
4. Device registration for push notifications

## Sync Strategy
1. Online-first approach
2. Conflict resolution (last-write-wins or manual)
3. Background sync for desktop/mobile
4. Delta updates to minimize data transfer

## Deployment
- **Web:** Traditional Django deployment
- **Desktop:** Auto-updating packages (AppImage, DMG, MSI)
- **Mobile:** App Store / Play Store
