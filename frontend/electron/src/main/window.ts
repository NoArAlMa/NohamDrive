import electron from "electron";
import path from "node:path";
import type { BrowserWindow as BrowserWindowType } from "electron";
const { app, BrowserWindow } = electron;
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow: BrowserWindowType | null = null;

const isDev = !app.isPackaged;
const preloadPath = isDev
  ? path.join(process.cwd(), "dist-electron/preload.js")
  : path.join(__dirname, "../../preload.js");

/**
 * Crée et configure la fenêtre principale
 */
export function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      webSecurity: true,
      nodeIntegration: false,
      preload: preloadPath,
    },
  });

  mainWindow.webContents.on("did-fail-load", () => {
    setTimeout(() => mainWindow?.reload(), 200);
  });

  setTimeout(() => {
    mainWindow?.loadURL("http://localhost:3000");
  }, 1000);

  return mainWindow;
}

/**
 * Retourne la fenêtre principale actuelle
 */
export function getMainWindow() {
  return mainWindow;
}
