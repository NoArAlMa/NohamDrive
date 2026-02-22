import updater from "electron-updater";
import log from "electron-log";
import electron from "electron";
import type { BrowserWindow } from "electron";

const { app, dialog } = electron;

const { autoUpdater } = updater;
/**
 * Configure et gère les mises à jour automatiques de l'application.
 * @param mainWindow La fenêtre principale de l'application.
 */
export function setupAutoUpdater(mainWindow: BrowserWindow) {
  // Désactive les mises à jour en mode développement
  if (!app.isPackaged) {
    log.info("AutoUpdater désactivé en mode dev");
    return;
  }

  // Configuration du feed de mise à jour (GitHub)
  autoUpdater.setFeedURL({
    provider: "github",
    owner: "NoArAlMa",
    repo: "NohamDrive",
    private: false,
  });

  // Désactive le téléchargement automatique pour contrôler l'expérience utilisateur
  autoUpdater.autoDownload = false;
  // Active le logging pour electron-updater
  autoUpdater.logger = log as any;
  (log as any).transports.file.level = "info";

  // Vérifie les mises à jour au démarrage
  autoUpdater.checkForUpdates();

  // Écoute les événements de mise à jour
  autoUpdater.on("checking-for-update", () => {
    log.info("Recherche de mise à jour...");
  });

  autoUpdater.on("update-available", () => {
    dialog
      .showMessageBox(mainWindow, {
        type: "info",
        title: "Mise à jour disponible",
        message:
          "Une nouvelle version de NohamDrive est disponible. Voulez-vous la télécharger maintenant ?",
        buttons: ["Télécharger", "Plus tard"],
        defaultId: 0,
      })
      .then(({ response }) => {
        if (response === 0) {
          log.info("Téléchargement de la mise à jour...");
          autoUpdater.downloadUpdate();
        }
      });
  });

  autoUpdater.on("update-not-available", () => {
    log.info("Aucune mise à jour disponible");
  });

  autoUpdater.on("update-downloaded", () => {
    dialog
      .showMessageBox(mainWindow, {
        type: "info",
        title: "Mise à jour prête",
        message:
          "La mise à jour est prête. L'application va redémarrer pour l’installer.",
        buttons: ["Redémarrer"],
      })
      .then(() => {
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
