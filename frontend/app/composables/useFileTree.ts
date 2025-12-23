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
      watch: [() => FSStore.currentPath],
    }
  );

  // On regarde le changement de valeur de currentPath pour refresh les dossiers
  // watch(
  //   () => FSStore.currentPath,
  //   () => {
  //     data.value = undefined;
  //     refresh();
  //   }
  // );

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
