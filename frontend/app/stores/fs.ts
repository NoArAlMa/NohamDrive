import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import { useCookie } from "#app";

export const useFSStore = defineStore("fs", () => {
  // Cookie
  const pathCookie = useCookie<string>("currentPath", {
    default: () => "/",
    maxAge: 60 * 60 * 24 * 7, // 1 semaine
  });

  // State synchronisé avec le cookie
  const currentPath = ref<string>(pathCookie.value || "/");

  // Synchronisation automatique
  watch(currentPath, (newPath) => {
    pathCookie.value = newPath;
  });

  // Actions
  const setCurrentPath = (newPath: string) => {
    currentPath.value = newPath.replace(/\/+/g, "/");
  };

  const goUp = () => {
    const parts = currentPath.value.split("/").filter(Boolean);
    if (parts.length > 0) {
      parts.pop();
      currentPath.value = parts.length ? `/${parts.join("/")}` : "/";
    }
  };

  const navigate = (path: string) => {
    if (path.startsWith("/")) {
      setCurrentPath(path);
    } else {
      setCurrentPath(`${currentPath.value}/${path}`);
    }
  };

  // Getters
  const currentDirName = computed(() => {
    const parts = currentPath.value.split("/").filter(Boolean);
    return parts.length ? parts[parts.length - 1] : "Root";
  });

  const isRoot = computed(() => currentPath.value === "/");

  return {
    currentPath,
    setCurrentPath,
    goUp,
    navigate,
    currentDirName,
    isRoot,
  };
});
