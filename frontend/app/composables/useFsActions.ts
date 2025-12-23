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
      const req = await $fetch<RenameFileResponse>("/storage/rename", {
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

  const del = async (item: ApiFileItem): Promise<void> => {
    const full_path = item.is_dir
      ? `${joinPath(FSStore.currentPath, item.name)}/`
      : joinPath(FSStore.currentPath, item.name);

    try {
      const req = await $fetch<GenericAPIResponse<null>>("/storage/object", {
        method: "DELETE",
        query: {
          folder_path: full_path,
        },
      });

      useFileTree().retryFetching();
      toast.add({ title: "On l'a supprimé", color: "success" });
    } catch (error: any) {
      const message =
        error.data?.statusMessage ||
        "Impossible de renommer le fichier/dossier.";
      toast.add({ title: "Erreur", description: message, color: "error" });
      throw error;
    }
  };

  const property = async (item: ApiFileItem) => {
    const full_path = item.is_dir
      ? `${joinPath(FSStore.currentPath, item.name)}/`
      : joinPath(FSStore.currentPath, item.name);

    try {
      const req = await $fetch<GenericAPIResponse<FileMetadata>>(
        "/storage/stats",
        {
          method: "GET",
          query: {
            object_path: full_path,
          },
        }
      );

      // TODO : Ouvrir le drawer
    } catch (error: any) {
      const message =
        error.data?.statusMessage ||
        "Impossible de renommer le fichier/dossier.";
      toast.add({ title: "Erreur", description: message, color: "error" });
      throw error;
    }
  };

  const terminal = (item: ApiFileItem) => {
    /* ... */
  };

  const download = async (item: ApiFileItem) => {
    const full_path = item.is_dir
      ? `${joinPath(FSStore.currentPath, item.name)}/`
      : joinPath(FSStore.currentPath, item.name);

    const encoded_path = full_path.split("/").map(encodeURIComponent).join("/");

    try {
      const API_URL = useRuntimeConfig().public.apiBaseUrl;
      const url = `${API_URL}/storage/download/${encoded_path}`;

      const response = await fetch(url, {
        method: "GET",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Le téléchargement a échoué");
      }

      // Utilise le nom de fichier suggéré par le backend
      const contentDisposition = response.headers.get("Content-Disposition");
      let filename = "fichier"; // Valeur par défaut

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      } else {
        // Si pas de Content-Disposition, génère un nom approprié
        if (item.is_dir) {
          filename = `${item.name}.zip`; // Ex: "docs.zip"
        } else {
          filename = full_path.split("/").pop() || "fichier";
        }
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error: any) {
      const message = error.message || "Le téléchargement a échoué";
      toast.add({ title: "Erreur", description: message, color: "error" });
      throw error;
    }
  };

  return { open, rename, del, property, terminal, download };
};
