import type { ApiFileItem } from "~~/shared/types/file_tree";

export const useFsActions = () => {
  const FSStore = useFSStore();
  const toast = useToast();
  const open = (item: ApiFileItem) => {
    if (item.is_dir) {
      FSStore.navigate(item.name);
    }
  };
  const rename = async (
    old_name: string,
    newName: string,
    item: ApiFileItem
  ): Promise<RenameFileResponse | null> => {
    const full_path = item.is_dir
      ? `${joinPath(FSStore.currentPath, old_name)}/`
      : joinPath(FSStore.currentPath, old_name);

    try {
      const req = await $fetch<RenameFileResponse>("/api/storage/rename", {
        method: "PATCH",
        body: {
          path: full_path,
          new_name: newName,
        },
      });

      useFileTree().retryFetching();
      toast.add({ title: "Renommé avec succès", color: "success" });
      return req;
    } catch (error: any) {
      const message =
        error.data?.statusMessage ||
        "Impossible de renommer le fichier/dossier.";
      toast.add({ title: "Erreur", description: message, color: "error" });
      throw error;
    }
  };
  const del = (item: ApiFileItem) => {
    /* ... */
  };
  const property = (item: ApiFileItem) => {
    /* ... */
  };
  const terminal = (item: ApiFileItem) => {
    /* ... */
  };
  const download = (item: ApiFileItem) => {
    /* ... */
  };

  return { open, rename, del, property, terminal, download };
};
