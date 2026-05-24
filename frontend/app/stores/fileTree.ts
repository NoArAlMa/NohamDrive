import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import { useFSStore } from "./fs";

export const useFileTree = defineStore("fileTree", () => {
  const FSStore = useFSStore();
  const AuthStore = useAuthStore();

  const emptyFileTree: ApiFileItem[] = [];
  const CACHE_TTL_MS = 15_000;
  const cache = new Map<
    string,
    { fetchedAt: number; response: GenericAPIResponse<ApiFileTreeData> }
  >();
  const data = ref<GenericAPIResponse<ApiFileTreeData> | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);
  let activeFetchId = 0;
  let abortController: AbortController | null = null;
  let inFlightPath: string | null = null;
  let inFlightPromise: Promise<void> | null = null;

  const fetchFileTree = async (
    options: { force?: boolean; revalidate?: boolean } = {},
  ): Promise<void> => {
    const path = FSStore.currentPath;
    const cachedEntry = cache.get(path);

    if (!options.force && cachedEntry) {
      data.value = cachedEntry.response;
      error.value = null;

      const isFresh = Date.now() - cachedEntry.fetchedAt < CACHE_TTL_MS;
      if (isFresh && !options.revalidate) {
        loading.value = false;
        return;
      }
    }

    if (!options.force && loading.value && inFlightPath === path && inFlightPromise) {
      return inFlightPromise;
    }

    abortController?.abort();
    abortController = new AbortController();
    const fetchId = ++activeFetchId;
    const requestFetch = import.meta.server ? useRequestFetch() : $fetch;

    try {
      loading.value = true;
      error.value = null;
      inFlightPath = path;
      inFlightPromise = (async () => {
        const response = await requestFetch<GenericAPIResponse<ApiFileTreeData>>(
          "/api/storage/tree",
          {
            query: { path },
            signal: abortController?.signal,
          },
        );
        if (fetchId !== activeFetchId) return;

        cache.set(path, { fetchedAt: Date.now(), response });
        data.value = response;
      })();

      await inFlightPromise;
    } catch (err) {
      if ((err as Error).name === "AbortError" || fetchId !== activeFetchId) {
        return;
      }
      error.value = err as Error;
    } finally {
      if (fetchId === activeFetchId) {
        loading.value = false;
        abortController = null;
        inFlightPath = null;
        inFlightPromise = null;
      }
    }
  };

  const reset = () => {
    abortController?.abort();
    abortController = null;
    activeFetchId++;
    cache.clear();
    data.value = null;
    error.value = null;
    loading.value = false;
    inFlightPath = null;
    inFlightPromise = null;
  };

  watch(
    [() => FSStore.currentPath, () => AuthStore.token],
    ([, tokenVal], [, previousToken]) => {
      if (!tokenVal) {
        reset();
        return;
      }
      if (previousToken && tokenVal !== previousToken) {
        cache.clear();
      }
      fetchFileTree();
    },
    { immediate: true },
  );
  const fileTree = computed<ApiFileItem[]>(
    () => data.value?.data?.items ?? emptyFileTree,
  );

  const hasError = computed(() => !!error.value);
  const errorStatus = computed(() => (error.value as any)?.statusCode);
  const errorMessage = computed(
    () =>
      (error.value as any)?.statusMessage ?? "Une erreur inconnue est survenue",
  );

  const totalElements = computed(() => data.value?.data?.total_items ?? 0);

  const retryFetching = async () => {
    await fetchFileTree({ force: true });
  };

  return {
    fileTree,
    loading,
    retryFetching,
    hasError,
    errorMessage,
    errorStatus,
    totalElements,
    reset,
  };
});
