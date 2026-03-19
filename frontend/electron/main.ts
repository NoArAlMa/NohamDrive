import electron from "electron";
import type { BrowserWindow as BrowserWindowType } from "electron";
import { setupAutoUpdater } from "./src/main/update.js";
import { createWindow } from "./src/main/window.js";
import { createTray } from "./src/tray.js";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { EventEmitter } from "events";

const { BrowserWindow, app, ipcMain } = electron;
const loadingEvents = new EventEmitter();

let splashWindow: BrowserWindowType | null = null;
let mainWindow: BrowserWindowType | null = null;
let isQuiting = false;

const isDev = !app.isPackaged;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function createMain() {
  // Create the browser window.
  mainWindow = createWindow();
  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
}

app.whenReady().then(async () => {
  createMain();

  // app.on("activate", function () {
  //   // On macOS it's common to re-create a window in the app when the
  //   // dock icon is clicked and there are no other windows open.
  //   if (BrowserWindow.getAllWindows().length === 0) createWindow();
  // });

  createTray(mainWindow!);
  setupAutoUpdater(mainWindow!);

  mainWindow?.on("close", (event: any) => {
    if (!isQuiting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });
});

ipcMain.handle("get-app-info", async () => ({
  isElectron: true,
  appVersion: app.getVersion(),
  platform: os.platform(),
  arch: os.arch(),
}));

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

process.on("uncaughtException", (error) => {
  console.error("Uncaught exception:", error);
});

process.on("unhandledRejection", (reason) => {
  console.error("Unhandled rejection:", reason);
});
