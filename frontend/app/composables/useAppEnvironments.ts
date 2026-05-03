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

  const checkElectron = async () => {
    if (typeof window !== "undefined" && window.electronAPI) {
      isElectron.value = true;
      try {
        appInfo.value = await window.electronAPI.getAppInfo();
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

  return { isElectron, appInfo };
};
