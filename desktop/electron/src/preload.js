const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// certain Electron APIs without exposing the entire API
contextBridge.exposeInMainWorld('electronAPI', {
    // Store operations
    store: {
        get: (key) => ipcRenderer.invoke('store-get', key),
        set: (key, value) => ipcRenderer.invoke('store-set', key, value),
        delete: (key) => ipcRenderer.invoke('store-delete', key),
        clear: () => ipcRenderer.invoke('store-clear')
    },
    
    // API operations
    api: {
        request: (config) => ipcRenderer.invoke('api-request', config)
    },
    
    // File operations
    file: {
        selectDirectory: () => ipcRenderer.invoke('select-directory'),
        selectFile: (options) => ipcRenderer.invoke('select-file', options)
    },
    
    // Notifications
    notifications: {
        show: (title, body) => ipcRenderer.send('show-notification', title, body)
    },
    
    // Navigation
    navigate: (path) => ipcRenderer.send('navigate', path),
    
    // Events
    on: (channel, callback) => {
        const validChannels = [
            'new-booking',
            'open-preferences',
            'update-available',
            'update-downloaded'
        ];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => callback(...args));
        }
    },
    
    // Platform info
    platform: process.platform,
    version: process.versions.electron
});
