export const useFileTree = () => {
  const fileTree = ref<ApiFileItem[]>([]);

  const fetchFileTree = async (path: string = "/") => {
    const { data } = await $fetch<ApiFileTreeResponse>(`/api/storage/tree`, {
      params: { path },
    });
    fileTree.value = data.items;
  };

  return { fileTree, fetchFileTree };
};
