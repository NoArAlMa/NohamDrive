export const useFileTree = () => {
  const FSStore = useFSStore();
  const {
    data,
    pending: loading,
    refresh,
    error,
  } = useAsyncData<ApiFileTreeResponse>(
    "file-tree",
    async () => {
      return $fetch("/storage/tree", {
        params: { path: FSStore.currentPath },
      });
    },
    {
      immediate: true,
    }
  );

  // On regarde le changement de valeur de currentPath pour refresh les dossiers
  watch(
    () => FSStore.currentPath,
    async () => {
      const startTime = Date.now();
      const timeout = setTimeout(() => {
        data.value = undefined; // Réinitialise si le chargement prend plus de 300ms
      }, 300);

      await refresh();
      clearTimeout(timeout);
    },
    { immediate: true }
  );

  const fileTree = computed(() => {
    return data.value?.data.items ?? [];
  });

  // Variable concernant les erreurs pour mieux les afficher en UI
  const hasError = computed(() => !!error.value);
  const errorStatus = computed(() => error.value?.statusCode);
  const errorMessage = computed(
    () => error.value?.statusMessage ?? "Une erreur inconnue est survenue"
  );

  // Fonction pour retry de récupérer les fichiers
  const retryFetching = () => {
    refresh();
  };

  return {
    fileTree,
    loading,
    retryFetching,
    hasError,
    errorMessage,
    errorStatus,
  };
};
