import type {
  CopyFilePayload,
  RenameFilePayload,
} from "~~/shared/types/file_request";
import type { ApiFileItem } from "~~/shared/types/file_tree";

export const useFsActions = () => {
  const FSStore = useFSStore();
  const toast = useToast();
  const { openDrawerWithProperties } = usePropertyDrawer();
  const open = (item: ApiFileItem) => {
    if (item.is_dir) {
      FSStore.navigate(item.name);
    }
  };

  const rename = async (
    old_name: string,
    newName: string,
    item: ApiFileItem
  ): Promise<GenericAPIResponse<RenameFilePayload>> => {
    const full_path = item.is_dir
      ? `${joinPath(FSStore.currentPath, old_name)}/`
      : joinPath(FSStore.currentPath, old_name);

    try {
      const req = await $fetch<GenericAPIResponse<RenameFilePayload>>(
        "/storage/rename",
        {
          method: "PATCH",
          body: {
            path: full_path,
            new_name: newName,
          },
        }
      );

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
      const req = await $fetch("/storage/stats", {
        method: "GET",
        query: {
          object_path: full_path,
        },
      });

      openDrawerWithProperties(req.data!);

      // TODO : Ouvrir le drawer
    } catch (error: any) {
      const message =
        error.data?.statusMessage || "Impossible de récupérer les stats.";
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
      const response = await fetch(`/storage/download/${encoded_path}`);

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "Le téléchargement a échoué");
      }

      const contentDisposition = response.headers.get("Content-Disposition");
      let filename =
        contentDisposition?.match(/filename="?([^"]+)"?/i)?.[1] ??
        (item.is_dir ? `${item.name}.zip` : item.name);

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();

      URL.revokeObjectURL(url);
    } catch (error: any) {
      toast.add({
        title: "Erreur",
        description: error.message || "Le téléchargement a échoué",
        color: "error",
      });
    }
  };

  const copy = async (
    item: ApiFileItem
  ): Promise<GenericAPIResponse<CopyFilePayload>> => {
    const full_path = item.is_dir
      ? `${joinPath(FSStore.currentPath, item.name)}/`
      : joinPath(FSStore.currentPath, item.name);

    try {
      const req = await $fetch<GenericAPIResponse<CopyFilePayload>>(
        "/storage/copy",
        {
          method: "POST",
          body: {
            source_path: full_path,
            destination_folder: FSStore.currentPath,
          },
        }
      );

      useFileTree().retryFetching();
      toast.add({ title: "Copié avec succès", color: "success" });
      return req;
    } catch (error: any) {
      const message =
        error.data?.statusMessage || "Impossible de copier le fichier/dossier.";
      toast.add({ title: "Erreur", description: message, color: "error" });
      throw error;
    }
  };

  const upload = async (files: File[]) => {
    if (!files || files.length === 0) return;

    const uploadPromises = files.map(async (file) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("path", FSStore.currentPath);

      return $fetch<GenericAPIResponse<null>>("/storage/upload", {
        method: "POST",
        body: formData,
        headers: {},
      })
        .then((res) => {
          console.log(`✅ Upload réussi pour ${file.name}`);
          return res;
        })
        .catch((error) => {
          const message =
            error.data?.statusMessage || `Impossible d'uploader ${file.name}.`;
          console.error(`❌ Erreur pour ${file.name}:`, message);
          toast.add({ title: "Erreur", description: message, color: "error" });
          throw error;
        });
    });

    // Attendre que tous les uploads soient terminés
    await Promise.all(uploadPromises);
    // Actualisation de l'explorateur
    useFileTree().retryFetching();
    toast.add({ title: "Upload réussi", color: "success" });
  };

  const compress = async (
    items: ApiFileItem[],
    destination_folder: string = FSStore.currentPath,
    output_base_name: string = "compressed_folder"
  ): Promise<void> => {
    const object_names = items.map((item) =>
      item.is_dir
        ? `${joinPath(FSStore.currentPath, item.name)}/`
        : joinPath(FSStore.currentPath, item.name)
    );

    try {
      const req = await $fetch<GenericAPIResponse<null>>("/storage/compress", {
        method: "POST",
        body: {
          objects: object_names,
          destination_folder,
          output_base_name,
        },
      });

      useFileTree().retryFetching();
      toast.add({ title: "Compression terminée", color: "success" });
    } catch (error: any) {
      const message =
        error.data?.statusMessage || "Impossible de compresser les fichiers.";
      toast.add({ title: "Erreur", description: message, color: "error" });
      throw error;
    }
  };

  const createFolder = async (
    folderName: string,
    currentPath: string = FSStore.currentPath
  ): Promise<void> => {
    try {
      const req = await $fetch<GenericAPIResponse<string>>("/storage/folder", {
        method: "POST",
        body: {
          currentPath,
          folderPath: folderName,
        },
      });

      useFileTree().retryFetching();
      toast.add({ title: "Dossier créé", color: "success" });
    } catch (error: any) {
      const message =
        error.data?.statusMessage ??
        `Impossible de créer le dossier "${folderName}".`;
      toast.add({ title: "Erreur", description: message, color: "error" });
      throw error;
    }
  };

  return {
    open,
    rename,
    del,
    property,
    terminal,
    download,
    copy,
    upload,
    compress,
    createFolder,
  };
};
