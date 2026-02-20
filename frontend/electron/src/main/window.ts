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

const NITRO_URL = "http://localhost:3000";
const RETRY_INTERVAL = 200; // ms entre chaque tentative
const MAX_RETRIES = 50; // sécurité → 50 * 200ms = 10s max

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

  let retries = 0;

  function tryLoadURL() {
    if (!mainWindow) return;

    mainWindow.loadURL(NITRO_URL).catch(() => {
      // si ça échoue, on retry après RETRY_INTERVAL
      retries++;
      if (retries <= MAX_RETRIES) {
        setTimeout(tryLoadURL, RETRY_INTERVAL);
      } else {
        console.error("Impossible de charger Nitro après plusieurs tentatives");
        // fallback : afficher une page locale
        mainWindow?.loadFile(path.join(__dirname, "offline.html"));
      }
    });
  }

  // Événement si la page ne peut pas charger (ex: serveur pas encore prêt)
  mainWindow.webContents.on("did-fail-load", () => {
    retries++;
    if (retries <= MAX_RETRIES) {
      setTimeout(tryLoadURL, RETRY_INTERVAL);
    } else {
      console.error("Impossible de charger Nitro après plusieurs tentatives");
      mainWindow?.loadFile(path.join(__dirname, "offline.html"));
    }
  });

  // Premier essai immédiat
  tryLoadURL();
  return mainWindow;
}

/**
 * Retourne la fenêtre principale actuelle
 */
export function getMainWindow() {
  return mainWindow;
}
