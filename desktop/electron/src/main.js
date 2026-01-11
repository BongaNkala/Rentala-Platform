const { app, BrowserWindow, Menu, Tray, nativeImage, ipcMain, shell, dialog, session } = require('electron');
const path = require('path');
const url = require('url');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');
const axios = require('axios');

// Initialize store
const store = new Store();

// Keep a global reference of the window object
let mainWindow;
let tray = null;
let isQuitting = false;

// Create the main browser window
function createWindow() {
    const icon = nativeImage.createFromPath(path.join(__dirname, '../resources/icon.png'));
    
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        icon: icon,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: true,
            devTools: process.env.NODE_ENV === 'development'
        },
        show: false,
        backgroundColor: '#ffffff',
        titleBarStyle: 'hiddenInset',
        frame: process.platform === 'darwin' ? true : false
    });

    // Load the app
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadURL(url.format({
            pathname: path.join(__dirname, '../public/index.html'),
            protocol: 'file:',
            slashes: true
        }));
    }

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        
        // Check for updates
        if (process.env.NODE_ENV !== 'development') {
            autoUpdater.checkForUpdatesAndNotify();
        }
    });

    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        // Open external links in default browser
        if (url.startsWith('http') && !url.includes('localhost')) {
            shell.openExternal(url);
            return { action: 'deny' };
        }
        return { action: 'allow' };
    });

    // Create application menu
    createApplicationMenu();
}

// Create application menu
function createApplicationMenu() {
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'New Booking',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        mainWindow.webContents.send('new-booking');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Preferences',
                    accelerator: 'CmdOrCtrl+,',
                    click: () => {
                        mainWindow.webContents.send('open-preferences');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Exit',
                    accelerator: 'CmdOrCtrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' },
                { role: 'selectAll' }
            ]
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        {
            label: 'Window',
            submenu: [
                { role: 'minimize' },
                { role: 'zoom' },
                { type: 'separator' },
                { role: 'front' },
                { type: 'separator' },
                {
                    label: 'Dashboard',
                    click: () => {
                        mainWindow.webContents.send('navigate', '/dashboard');
                    }
                },
                {
                    label: 'My Bookings',
                    click: () => {
                        mainWindow.webContents.send('navigate', '/bookings');
                    }
                },
                {
                    label: 'Search',
                    click: () => {
                        mainWindow.webContents.send('navigate', '/search');
                    }
                }
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'Documentation',
                    click: () => {
                        shell.openExternal('https://docs.rentala.com');
                    }
                },
                {
                    label: 'Report Issue',
                    click: () => {
                        shell.openExternal('https://github.com/rentala/desktop/issues');
                    }
                },
                { type: 'separator' },
                {
                    label: 'About Rentala',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'About Rentala',
                            message: 'Rentala Desktop v1.0.0',
                            detail: 'Rentala Desktop Application\nBuilt with Electron\n© 2024 Rentala'
                        });
                    }
                }
            ]
        }
    ];

    // Add specific menu for macOS
    if (process.platform === 'darwin') {
        template.unshift({
            label: app.name,
            submenu: [
                { role: 'about' },
                { type: 'separator' },
                { role: 'services' },
                { type: 'separator' },
                { role: 'hide' },
                { role: 'hideOthers' },
                { role: 'unhide' },
                { type: 'separator' },
                { role: 'quit' }
            ]
        });
    }

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// Create system tray
function createTray() {
    const icon = nativeImage.createFromPath(path.join(__dirname, '../resources/tray.png'));
    tray = new Tray(icon);
    
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Show Rentala',
            click: () => {
                mainWindow.show();
            }
        },
        {
            label: 'New Booking',
            click: () => {
                mainWindow.show();
                mainWindow.webContents.send('new-booking');
            }
        },
        { type: 'separator' },
        {
            label: 'Quit',
            click: () => {
                isQuitting = true;
                app.quit();
            }
        }
    ]);
    
    tray.setToolTip('Rentala');
    tray.setContextMenu(contextMenu);
    
    tray.on('click', () => {
        mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    });
}

// IPC Handlers
function setupIpcHandlers() {
    // Store operations
    ipcMain.handle('store-get', (event, key) => {
        return store.get(key);
    });
    
    ipcMain.handle('store-set', (event, key, value) => {
        store.set(key, value);
    });
    
    ipcMain.handle('store-delete', (event, key) => {
        store.delete(key);
    });
    
    ipcMain.handle('store-clear', () => {
        store.clear();
    });
    
    // API requests
    ipcMain.handle('api-request', async (event, config) => {
        try {
            const response = await axios({
                ...config,
                baseURL: store.get('api-url') || 'http://localhost:8000/api/v1'
            });
            return { data: response.data, status: response.status };
        } catch (error) {
            return { error: error.message, status: error.response?.status || 500 };
        }
    });
    
    // File operations
    ipcMain.handle('select-directory', async () => {
        const result = await dialog.showOpenDialog(mainWindow, {
            properties: ['openDirectory']
        });
        return result.filePaths[0];
    });
    
    ipcMain.handle('select-file', async (event, options) => {
        const result = await dialog.showOpenDialog(mainWindow, {
            ...options,
            properties: ['openFile']
        });
        return result.filePaths[0];
    });
    
    // Notifications
    ipcMain.on('show-notification', (event, title, body) => {
        if (process.platform === 'win32') {
            // Windows notification
            const notification = {
                title: title,
                body: body,
                icon: path.join(__dirname, '../resources/icon.png')
            };
            new Notification(notification).show();
        }
        // macOS/Linux notifications are handled differently
    });
}

// App lifecycle
app.whenReady().then(() => {
    createWindow();
    createTray();
    setupIpcHandlers();
    
    // Auto-launch setting
    app.setLoginItemSettings({
        openAtLogin: store.get('auto-start', false)
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('before-quit', () => {
    isQuitting = true;
});

// Auto updater events
autoUpdater.on('update-available', () => {
    mainWindow.webContents.send('update-available');
});

autoUpdater.on('update-downloaded', () => {
    mainWindow.webContents.send('update-downloaded');
});

autoUpdater.on('error', (error) => {
    console.error('Auto updater error:', error);
});
