import { ref, onMounted } from "vue";

export const useElectron = () => {
  const isElectron = ref(false);
  const appInfo = ref<null | {
    isElectron: boolean;
    appVersion: string;
    platform: string;
    arch: string;
  }>(null);

  const checkElectron = async () => {
    // window.electronAPI peut exister même avant onMounted
    if (typeof window !== "undefined" && window.electronAPI) {
      isElectron.value = true;
      try {
        appInfo.value = await window.electronAPI.getAppInfo();
      } catch (err) {
        console.error("Failed to get app info", err);
      }
    }
  };

  onMounted(checkElectron);
  checkElectron();

  return { isElectron, appInfo };
};
