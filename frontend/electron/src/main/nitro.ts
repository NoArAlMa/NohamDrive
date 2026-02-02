import { spawn, ChildProcessWithoutNullStreams } from "node:child_process";
import path from "node:path";
import log from "electron-log";
import { app } from "electron";

let nitroProcess: ChildProcessWithoutNullStreams | null = null;

/**
 * Démarre le serveur Nitro (Nuxt) en arrière-plan.
 */
export function startNitro() {
  if (!app.isPackaged) {
    log.info(`[Nitro] Nitro désactivé en mode DEV`);
    return null;
  }
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

  return nitroProcess;
}

/**
 * Arrête le serveur Nitro s'il est en cours d'exécution.
 */
export function stopNitro() {
  if (nitroProcess) {
    nitroProcess.kill();
    nitroProcess = null;
  }
}
