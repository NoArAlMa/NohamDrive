import { BrowserWindow, app, shell, Menu } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const isDev = !app.isPackaged;

const preloadPath = isDev
  ? path.join(process.cwd(), "dist-electron/preload.js")
  : path.join(__dirname, "../../preload.js");

const url = isDev ? "http://localhost:3000" : "https://nsi.alexandre-larue.fr";

export function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    minHeight: 600,
    minWidth: 1100,
    height: 800,
    autoHideMenuBar: true,
    show: false,
    webPreferences: {
      contextIsolation: true,
      webSecurity: true,
      nodeIntegration: false,
      preload: preloadPath,
    },
  });

  Menu.setApplicationMenu(null);

  // Pour les fenêtres _blank => Vers le navigateur
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  // Eviter d'aller sur d'autres sites
  win.webContents.on("will-navigate", (event, url) => {
    const allowed = ["http://localhost:3000", "https://nsi.alexandre-larue.fr"];

    if (!allowed.some((domain) => url.startsWith(domain))) {
      event.preventDefault();
    }
  });

  win.loadURL(url + "/home");

  win.webContents.once("did-finish-load", () => {
    win.show();
  });
  return win;
}

let loadingWindow: BrowserWindow | null = null;

export function createSplashWindow() {
  loadingWindow = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    alwaysOnTop: true,
    resizable: false,
    show: true,
    modal: false,

    webPreferences: {
      preload: preloadPath,
      partition: "persist:splash", // Utilise une partition dédiée
      nodeIntegration: false,
      contextIsolation: true,
    },
  });
  loadingWindow.loadFile(path.join(__dirname, "../html/loading.html"));

  return loadingWindow;
}

let trayWindow: BrowserWindow | null = null;

export function createTrayWindow() {
  trayWindow = new BrowserWindow({
    width: 300,
    height: 400,
    show: false,
    frame: false, // pas de barre Windows
    resizable: false,
    movable: false,
    fullscreenable: false,
    skipTaskbar: true,
    alwaysOnTop: true,
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  trayWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  trayWindow.setAlwaysOnTop(true, "screen-saver");

  trayWindow.loadURL(url + "/tray?electron=true");

  // Cache quand on clique ailleurs
  trayWindow.on("blur", () => {
    trayWindow?.hide();
  });

  trayWindow.on("show", () => {
    trayWindow?.focus();
  });

  return trayWindow;
}
