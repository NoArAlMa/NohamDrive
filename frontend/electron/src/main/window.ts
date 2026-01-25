import { BrowserWindow } from "electron";

let mainWindow: BrowserWindow | null = null;

/**
 * Crée et configure la fenêtre principale de l'application.
 */
export function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      webSecurity: true,
    },
  });

  // Petit délai pour laisser Nitro démarrer avant de charger l'URL
  setTimeout(() => {
    mainWindow?.loadURL("http://localhost:3000");
  }, 1000);

  return mainWindow;
}

/**
 * Retourne la fenêtre principale actuelle.
 */
export function getMainWindow() {
  return mainWindow;
}
