import { defineStore } from "pinia";
import { computed, reactive, ref } from "vue";
import type { SyncStatusResponse } from "~/composables/useSync";

type SyncTaskType =
  | "upload"
  | "download"
  | "delete"
  | "move"
  | "rename"
  | "unknown";

type ActiveTask = {
  id: string;
  type: SyncTaskType;
  rawPath: string;
  canonicalPath: string;
  startedAt: number;
};

function normalizePathLikeCloud(input: string) {
  const raw = String(input ?? "");
  const trimmed = raw.trim();
  if (!trimmed) return "/";

  let p = trimmed.replace(/\\/g, "/");
  if (!p.startsWith("/")) p = `/${p}`;
  p = p.replace(/\/{2,}/g, "/");
  if (p.length > 1 && p.endsWith("/")) p = p.slice(0, -1);
  return p;
}

function ensureDirPath(path: string) {
  const p = normalizePathLikeCloud(path);
  if (p === "/") return "/";
  return p.endsWith("/") ? p : `${p}/`;
}

export const useSyncerActivityStore = defineStore("syncerActivity", () => {
  const connected = ref(false);
  const lastEventAt = ref<number | null>(null);

  const pathAliases = reactive(new Map<string, string>());
  const activeTasksByPath = reactive(new Map<string, ActiveTask[]>());

  function setConnected(value: boolean) {
    connected.value = value;
  }

  function canonicalizePath(input: string) {
    let p = normalizePathLikeCloud(input);
    for (let i = 0; i < 5; i++) {
      const aliased = pathAliases.get(p);
      if (!aliased || aliased === p) break;
      p = normalizePathLikeCloud(aliased);
    }
    return p;
  }

  function upsertTask(task: ActiveTask) {
    const key = task.canonicalPath;
    const existing = activeTasksByPath.get(key) ?? [];
    const idx = existing.findIndex((t) => t.id === task.id);

    if (idx >= 0) existing[idx] = task;
    else existing.push(task);

    activeTasksByPath.set(key, existing);
  }

  function removeTaskById(taskId: string) {
    for (const [path, tasks] of activeTasksByPath.entries()) {
      const next = tasks.filter((t) => t.id !== taskId);
      if (next.length !== tasks.length) {
        if (next.length) activeTasksByPath.set(path, next);
        else activeTasksByPath.delete(path);
      }
    }
  }

  function inferTaskType(input: unknown): SyncTaskType {
    const t = String(input ?? "").toLowerCase();
    if (t === "upload") return "upload";
    if (t === "download") return "download";
    if (t === "delete") return "delete";
    if (t === "move") return "move";
    if (t === "rename") return "rename";
    return "unknown";
  }

  function migratePath(fromPathRaw: string, toPathRaw: string) {
    const from = canonicalizePath(fromPathRaw);
    const to = canonicalizePath(toPathRaw);
    if (from === to) return;

    pathAliases.set(from, to);

    const tasks = activeTasksByPath.get(from);
    if (!tasks?.length) return;

    activeTasksByPath.delete(from);
    for (const t of tasks) {
      upsertTask({ ...t, rawPath: toPathRaw, canonicalPath: to });
    }
  }

  function ingestEvent(rawEvent: any) {
    if (!rawEvent) return;
    lastEventAt.value = Date.now();

    const eventName = rawEvent?.event ?? rawEvent?.type;
    if (!eventName) return;

    if (eventName === "task_queued" || eventName === "task_started") {
      const task = rawEvent?.task;
      if (!task?.id || !task?.path) return;
      upsertTask({
        id: String(task.id),
        type: inferTaskType(task.type),
        rawPath: String(task.path),
        canonicalPath: canonicalizePath(task.path),
        startedAt: Date.now(),
      });
      return;
    }

    if (eventName === "task_done") {
      const task = rawEvent?.task;
      if (task?.id) removeTaskById(String(task.id));
      return;
    }

    if (eventName === "local_upload_echo") {
      const localPath = rawEvent?.local_path;
      const remotePath = rawEvent?.remote_path;
      if (!localPath || !remotePath) return;
      migratePath(String(localPath), String(remotePath));
      return;
    }

    if (eventName === "file_moved") {
      const source = rawEvent?.source_path;
      const dest = rawEvent?.destination_path;
      if (!source || !dest) return;
      migratePath(String(source), String(dest));
      return;
    }
  }

  function hydrateFromStatus(status: SyncStatusResponse | null) {
    if (!status) return;
    const queued = Array.isArray(status.queued_tasks) ? status.queued_tasks : [];
    for (const task of queued) {
      if (!task?.id || !task?.path) continue;
      upsertTask({
        id: String(task.id),
        type: inferTaskType(task.type),
        rawPath: String(task.path),
        canonicalPath: canonicalizePath(task.path),
        startedAt: Date.now(),
      });
    }
  }

  function hasActiveTaskForPath(path: string) {
    const key = canonicalizePath(path);
    return (activeTasksByPath.get(key)?.length ?? 0) > 0;
  }

  function hasActiveTaskUnderDir(dirPath: string) {
    const prefix = ensureDirPath(dirPath);
    for (const key of activeTasksByPath.keys()) {
      if (key === prefix.slice(0, -1) || key.startsWith(prefix)) return true;
    }
    return false;
  }

  function getStatus(path: string, isDir = false): "syncing" | "synced" {
    if (isDir) return hasActiveTaskUnderDir(path) ? "syncing" : "synced";
    return hasActiveTaskForPath(path) ? "syncing" : "synced";
  }

  const activeTaskCount = computed(() => {
    let count = 0;
    for (const tasks of activeTasksByPath.values()) count += tasks.length;
    return count;
  });

  return {
    connected,
    lastEventAt,
    activeTaskCount,
    setConnected,
    ingestEvent,
    hydrateFromStatus,
    canonicalizePath,
    getStatus,
  };
});
