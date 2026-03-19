import { Tray, Menu, app } from "electron";
import type { Tray as TrayType } from "electron";
import { BrowserWindow } from "electron";
import path from "node:path";
import { createTrayWindow } from "./main/window.js";

let tray: TrayType | null;
const isDev = !app.isPackaged;

const iconPath = isDev
  ? path.join(process.cwd(), "electron/assets/icons/nh-icon.ico")
  : path.join(process.resourcesPath, "assets/icons/nh-icon.ico");

let trayWindow: BrowserWindow | null = null;

function getTrayPosition() {
  if (!tray || !trayWindow) return { x: 0, y: 0 };
  const MARGIN = 10;
  const trayBounds = tray.getBounds();
  const windowBounds = trayWindow.getBounds();

  const x = Math.round(
    trayBounds.x + trayBounds.width / 2 - windowBounds.width / 2,
  );

  const isBottom = trayBounds.y > 500;

  const y = isBottom
    ? trayBounds.y - windowBounds.height - MARGIN
    : trayBounds.y + trayBounds.height + MARGIN;

  return { x, y };
}

export function createTray(win: BrowserWindow) {
  tray = new Tray(iconPath);

  trayWindow = createTrayWindow();

  const contextMenu = Menu.buildFromTemplate([
    { label: "Ouvrir", click: () => win.show() },
    {
      label: "Paramètres",
      click: () => {},
    },
    { type: "separator" },
    {
      label: "Quitter",
      click: () => {
        if (tray) {
          tray.destroy();
          tray = null;
        }
        BrowserWindow.getAllWindows().forEach((w) => w.destroy());

        app.quit();
      },
    },
  ]);

  tray.on("click", () => {
    if (!trayWindow) return;

    if (trayWindow.isVisible()) {
      trayWindow.hide();
    } else {
      const { x, y } = getTrayPosition();
      trayWindow.setPosition(x, y, false);
      trayWindow.show();
      trayWindow.focus();
    }
  });

  tray.setToolTip("NohamDrive");
  tray.setContextMenu(contextMenu);
}
