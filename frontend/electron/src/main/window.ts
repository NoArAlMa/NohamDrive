import { BrowserWindow, app } from "electron";
import path from "node:path";

import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow: BrowserWindow | null = null;
const isDev = !app.isPackaged;

const preloadPath = isDev
  ? path.join(process.cwd(), "dist-electron/preload.js") 
  : path.join(__dirname, "../../preload.js"); 
/**
 * Crée et configure la fenêtre principale de l'application.
 */
export function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: false,

    webPreferences: {
      contextIsolation: true,
      webSecurity: true,
      nodeIntegration: false,
      preload: preloadPath,
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
