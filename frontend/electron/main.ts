import electron from "electron";
import { setupAutoUpdater } from "./src/main/update.js";
import { createWindow } from "./src/main/window.js";
import { startNitro, stopNitro } from "./src/main/nitro.js";
import os from "node:os";

const { BrowserWindow, app, ipcMain } = electron;

/**
 * Nettoie les ressources avant la fermeture de l'application.
 */
function cleanup() {
  stopNitro();
}

/**
 * Point d'entrée de l'application Electron.
 */
app.whenReady().then(() => {
  const mainWindow = createWindow();
  startNitro();
  setupAutoUpdater(mainWindow);
});



ipcMain.handle("get-app-info", async () => {
  return {
    isElectron: true,
    appVersion: app.getVersion(),
    platform: os.platform(),
    arch: os.arch(),
  };
});

app.on("window-all-closed", () => {
  cleanup();
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", cleanup);

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
