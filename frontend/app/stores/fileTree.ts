import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import { useFSStore } from "./fs";

export const useFileTree = defineStore("fileTree", () => {
  const FSStore = useFSStore();
  const data = ref<GenericAPIResponse<ApiFileTreeData> | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  const fetchFileTree = async () => {
    if (loading.value) return;
    try {
      loading.value = true;
      data.value = await $fetch("/storage/tree", {
        params: { path: FSStore.currentPath },
      });
    } catch (err) {
      error.value = err as Error;
    } finally {
      loading.value = false;
    }
  };

  // Charger les données au montage et quand currentPath change
  watch(
    () => FSStore.currentPath,
    () => fetchFileTree(),
    { immediate: true },
  );

  const fileTree = computed<ApiFileItem[]>(() => {
    return [...(data.value?.data?.items ?? [])];
  });

  const hasError = computed(() => !!error.value);
  const errorStatus = computed(() => (error.value as any)?.statusCode);
  const errorMessage = computed(
    () =>
      (error.value as any)?.statusMessage ?? "Une erreur inconnue est survenue",
  );

  const totalElements = computed(() => data.value?.data?.total_items ?? 0);

  const retryFetching = async () => {
    if (loading.value) return;
    await fetchFileTree();
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
});
