import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import { useCookie } from "#app";

export const useFSStore = defineStore("fs", () => {
  // Cookie
  const pathCookie = useCookie<string>("currentPath", {
    default: () => "/",
    maxAge: 60, // 1 semaine
  });

  const fileTreeStore = useFileTree();

  // State synchronisé avec le cookie
  const currentPath = ref<string>(pathCookie.value || "/");

  // Synchronisation automatique
  watch(currentPath, (newPath) => {
    pathCookie.value = newPath;
  });

  // Actions
  const navigate = (inputPath: string) => {
    if (fileTreeStore.loading) return;

    const newPath = resolvePath(inputPath, currentPath.value);

    if (newPath === currentPath.value) return;
    console.log("NEWPATH :", newPath, "CURRENTPATH:", currentPath.value);

    currentPath.value = newPath;
  };

  const goUp = () => {
    navigate("..");
  };

  const setCurrentPath = (path: string) => {
    if (fileTreeStore.loading) return;

    currentPath.value = path;
  };

  // Getters
  const currentDirName = computed(() => {
    const parts = currentPath.value.split("/").filter(Boolean);
    return parts.length ? parts.at(-1)! : "Root";
  });

  const isRoot = computed(() => currentPath.value === "/");

  const generateBreadcrumbItems = () => {
    const parts = currentPath.value.split("/").filter((part) => part !== "");
    const items = parts.map((part, index) => {
      const pathSoFar = parts.slice(0, index + 1).join("/");
      return {
        label: part,
        path: pathSoFar,
      };
    });

    // Ajoute toujours la racine ("/") en premier
    return [
      {
        label: "Mes fichiers",
        path: "/",
      },
      ...items,
    ];
  };

  return {
    currentPath,
    setCurrentPath,
    resolvePath,
    goUp,
    navigate,
    currentDirName,

    isRoot,
    generateBreadcrumbItems,
  };
});
