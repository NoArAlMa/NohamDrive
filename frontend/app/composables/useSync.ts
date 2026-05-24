export type SyncStatusResponse = {
  status: "running" | "paused" | "stopped";
  paused: boolean;
  watcher_running: boolean;
  sse_connected: boolean;
  watched_folder: string;
  queue_size: number;
  queued_tasks: any[];
  auto_start: boolean;
};

const SYSTEM_ROUTES = {
  status: "/api/syncer/status-sync",
  start: "/api/syncer/start-sync",
  pause: "/api/syncer/stop-sync",
};

export function useSyncState() {
  const status = useState<SyncStatusResponse | null>("sync-status", () => null);
  const loading = useState<boolean>("sync-loading", () => false);
  const auto_sync = useCookie<boolean>("auto_sync", { default: () => false });

  const autoStart = computed({
    get: () => status.value?.auto_start ?? false,
    set: async (value: boolean) => {
      await setAutoStart(value);
    },
  });

  const enabled = useCookie<boolean>("sync_enabled", {
    default: () => true,
    watch: true,
  });

  async function refresh() {
    try {
      status.value = await $fetch<SyncStatusResponse>(SYSTEM_ROUTES.status);
    } catch (e) {
      console.error("Failed to load sync status", e);
    }
  }

  async function start() {
    if (loading.value) return;
    loading.value = true;

    try {
      status.value = await $fetch("/api/syncer/start-sync", {
        method: "POST",
      });

      enabled.value = true;
    } finally {
      loading.value = false;
    }
  }

  async function pause() {
    if (loading.value) return;
    loading.value = true;

    try {
      status.value = await $fetch("/api/syncer/stop-sync", {
        method: "POST",
      });

      enabled.value = false;
    } finally {
      loading.value = false;
    }
  }

  async function toggle() {
    return enabled.value ? pause() : start();
  }

  async function setAutoStart(value: boolean) {
    if (loading.value) return;
    loading.value = true;

    try {
      const res = await $fetch<SyncStatusResponse>("/api/syncer/settings", {
        method: "PATCH",
        body: {
          auto_start: value,
        },
      });

      // update local state immediately
      if (status.value) {
        status.value.auto_start = value;
      } else {
        status.value = res;
      }
    } catch (e) {
      console.error("Failed to update auto_start", e);
    } finally {
      loading.value = false;
    }
  }

  return {
    status,
    loading,
    enabled,
    autoStart,
    refresh,
    start,
    pause,
    toggle,
    setAutoStart,
  };
}
