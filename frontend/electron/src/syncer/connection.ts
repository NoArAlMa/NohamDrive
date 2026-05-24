import fs from "fs";
import path from "path";
import os from "os";

const runtimePath = path.join(
  os.tmpdir(),
  "NohamDriveSyncer",
  "nohamdrive_runtime.json",
);

interface RuntimeFile {
  token: string;
  started_at: Date;
  port: string;
  host: string;
}

let runtime: RuntimeFile | null = null;

export function loadRuntime() {
  const raw = fs.readFileSync(runtimePath, "utf-8");
  runtime = JSON.parse(raw);
  return runtime;
}

export function getRuntime() {
  return runtime;
}
