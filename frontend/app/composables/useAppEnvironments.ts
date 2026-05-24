import { getCurrentInstance, onMounted, ref } from "vue";

export const useElectron = () => {
  const isElectron = ref(
    import.meta.client && typeof window !== "undefined" && !!window.electronAPI,
  );
  const appInfo = ref<null | {
    isElectron: boolean;
    appVersion: string;
    platform: string;
    arch: string;
  }>(null);

  const runtime = ref<null | {
    host: string;
    port: string;
    token: string;
    started_at: string;
  }>(null);

  const registerRuntime = async () => {
    await $fetch("/api/syncer/register-runtime", {
      method: "POST",
      body: runtime.value,
    });
  };

  const checkElectron = async () => {
    if (typeof window !== "undefined" && window.electronAPI) {
      isElectron.value = true;
      try {
        appInfo.value = await window.electronAPI.getAppInfo();
        runtime.value = await window.electronAPI.getRuntime();
        await registerRuntime();
      } catch (err) {
        console.error("Failed to get app info", err);
      }
    }
  };

  if (getCurrentInstance()) {
    onMounted(checkElectron);
  } else if (import.meta.client) {
    checkElectron();
  }

  return { isElectron, appInfo, runtime };
};
