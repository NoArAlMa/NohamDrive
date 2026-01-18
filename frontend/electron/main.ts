import * as path from "node:path";
import { app, BrowserWindow } from "electron";
import { spawn } from "node:child_process";

let mainWindow: BrowserWindow | null = null;
let nitroProcess = null;

function startNitro() {
  nitroProcess = spawn(
    "node",
    [path.join(process.resourcesPath, "server/index.mjs")],
    {
      env: { PORT: "3000", NODE_ENV: "production" },
      stdio: "pipe",
      cwd: path.join(process.resourcesPath, "server"),
    },
  );
  nitroProcess.stdout.on("data", (data) => console.log(`Nitro: ${data}`));
  nitroProcess.stderr.on("data", (data) =>
    console.error(`Nitro Error: ${data}`),
  );
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      webSecurity: true,
      contextIsolation: true,
    },
  });
  startNitro();
  setTimeout(() => {
    mainWindow!.loadURL("http://localhost:3000"); // Charge Nitro après 3 secondes
  }, 1000);
}

app.whenReady().then(createWindow);
