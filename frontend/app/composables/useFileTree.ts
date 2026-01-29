export const useFileTree = () => {
  const FSStore = useFSStore();
  const {
    data,
    pending: loading,
    refresh,
    error,
  } = useAsyncData<GenericAPIResponse<ApiFileTreeData>>(
    "file-tree",
    async () => {
      return $fetch("/storage/tree", {
        params: { path: FSStore.currentPath },
      });
    },
    {
      immediate: true,
      watch: [() => FSStore.currentPath],
      lazy: true,
    },
  );

  const fileTree = computed<ApiFileItem[]>(() => {
    return data.value?.data?.items ?? [];
  });

  // Variable concernant les erreurs pour mieux les afficher en UI
  const hasError = computed(() => !!error.value);
  const errorStatus = computed(() => error.value?.statusCode);
  const errorMessage = computed(
    () => error.value?.statusMessage ?? "Une erreur inconnue est survenue",
  );

  const totalElements = computed(() => data.value?.data?.total_items ?? 0);

  // Fonction pour retry de récupérer les fichiers
  const retryFetching = () => {
    if (loading.value) return;
    refresh();
  };

  return {
    fileTree,
    loading,
    retryFetching,
    hasError,
    errorMessage,
    errorStatus,
    totalElements,
  };
};
