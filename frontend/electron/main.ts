import * as path from "node:path";
import { app, BrowserWindow, dialog } from "electron";
import { spawn, ChildProcessWithoutNullStreams } from "node:child_process";

import log from "electron-log";

import updater from "electron-updater";
const { autoUpdater } = updater;

autoUpdater.setFeedURL({
  provider: "github",
  owner: "NoArAlMa",
  repo: "NohamDrive",
  private: false,
});

autoUpdater.logger = log as any;
(log as any).transports.file.level = "info";

let mainWindow: BrowserWindow | null = null;
let nitroProcess: ChildProcessWithoutNullStreams | null = null;

/**
 * Démarre le serveur Nitro (Nuxt) embarqué
 */
function startNitro() {
  const serverPath = path.join(process.resourcesPath, "server");

  nitroProcess = spawn("node", ["index.mjs"], {
    cwd: serverPath,
    env: {
      NODE_ENV: "production",
      PORT: "3000",
    },
    stdio: "pipe",
  });

  nitroProcess.stdout.on("data", (data) =>
    log.info(`[Nitro] ${data.toString()}`),
  );

  nitroProcess.stderr.on("data", (data) =>
    log.error(`[Nitro ERROR] ${data.toString()}`),
  );

  nitroProcess.on("exit", (code) => {
    log.warn(`Nitro process exited with code ${code}`);
  });
}

/**
 * Crée la fenêtre principale
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      webSecurity: true,
    },
  });

  startNitro();

  // Petit délai pour laisser Nitro démarrer
  setTimeout(() => {
    mainWindow?.loadURL("http://localhost:3000");
  }, 1000);
}

/**
 * Auto-updater (désactivé en dev)
 */
function setupAutoUpdater() {
  if (!app.isPackaged) {
    log.info("AutoUpdater désactivé en mode dev");
    return;
  }

  autoUpdater.autoDownload = false;
  autoUpdater.checkForUpdates();

  autoUpdater.on("checking-for-update", () => {
    log.info("Recherche de mise à jour...");
  });

  autoUpdater.on("update-available", () => {
    dialog
      .showMessageBox(mainWindow!, {
        type: "info",
        title: "Mise à jour disponible",
        message:
          "Une nouvelle version de NohamDrive est disponible. Voulez-vous la télécharger maintenant ?",
        buttons: ["Télécharger", "Plus tard"],
        defaultId: 0,
      })
      .then(({ response }) => {
        if (response === 0) {
          autoUpdater.downloadUpdate();
        }
      });
  });

  autoUpdater.on("update-not-available", () => {
    log.info("Aucune mise à jour disponible");
  });

  autoUpdater.on("update-downloaded", () => {
    dialog
      .showMessageBox(mainWindow!, {
        type: "info",
        title: "Mise à jour prête",
        message:
          "La mise à jour est prête. L'application va redémarrer pour l’installer.",
        buttons: ["Redémarrer"],
      })
      .then(() => {
        cleanup();
        autoUpdater.quitAndInstall();
      });
  });

  autoUpdater.on("error", (err) => {
    log.error("Erreur auto-updater:", err);
    dialog.showErrorBox(
      "Erreur de mise à jour",
      "Impossible de vérifier les mises à jour.\n" + err.message,
    );
  });
}

/**
 * Nettoyage avant fermeture / update
 */
function cleanup() {
  if (nitroProcess) {
    nitroProcess.kill();
    nitroProcess = null;
  }
}

/**
 * Lifecycle Electron
 */
app.whenReady().then(() => {
  createWindow();
  setupAutoUpdater();
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
