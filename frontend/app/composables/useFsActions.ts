import { LazyFileExplorerView } from "#components";
import type { Toast } from "@nuxt/ui/runtime/composables/useToast.js";
import type {
  CompressFilePayload,
  CompressFileResponse,
  CopyFilePayload,
  RenameFilePayload,
} from "~~/shared/types/file_request";
import type { ApiFileItem } from "~~/shared/types/file_tree";

export const useFsActions = () => {
  const FSStore = useFSStore();
  const toast = useToast();

  const overlay = useOverlay();

  const open = async (item: ApiFileItem) => {
    if (item.is_dir) {
      FSStore.navigate(item.name);
    } else {
      const fullPath = `${joinPath(FSStore.currentPath, item.name)}`;
      const cleanPath = fullPath.replace(/^\/+/, "");
      let loadingToast: Toast | undefined;
      loadingToast = toast.add({
        title: "En cours d'ouverture...",
        color: "neutral",
        duration: 0,
        close: false,
        ui: { icon: "animate-spin" },
        icon: "material-symbols:progress-activity",
      });
      try {
        const response = await $fetch(`/storage/preview/${cleanPath}`, {
          responseType: "blob",
        });
        const blob = new Blob([response], { type: response.type });
        const fileName = item.name;

        // Crée un objet File
        const file = new File([blob], fileName, { type: blob.type });

        const viewModal = overlay.create(LazyFileExplorerView, {
          props: {
            fileName: fileName,
            file: file,
          },
        });
        viewModal.open();
        if (loadingToast) toast.remove(loadingToast.id);
      } catch (error: any) {
        if (loadingToast) toast.remove(loadingToast.id);
        toast.add({
          title: "Erreur",
          description:
            error.data?.statusMessage ??
            "Impossible de supprimer le fichier/dossier.",
          color: "error",
          icon: "material-symbols:error-outline-rounded",
        });

        throw error;
      }
    }
  };

  const rename = async (
    old_name: string,
    newName: string,
    item: ApiFileItem,
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
        },
      );

      useFileTree().retryFetching();
      return req;
    } catch (error: any) {
      const message =
        error.data?.data.message ||
        "Impossible de renommer le fichier/dossier.";
      toast.add({
        title: "Erreur",
        icon: "material-symbols:error-outline-rounded",
        description: message,
        color: "error",
      });
      throw error;
    }
  };

  const del = async (
    item: ApiFileItem,
    options?: {
      silent?: boolean;
    },
  ): Promise<void> => {
    const full_path = item.is_dir
      ? `${joinPath(FSStore.currentPath, item.name)}/`
      : joinPath(FSStore.currentPath, item.name);

    let loadingToast: Toast | undefined;

    if (!options?.silent) {
      loadingToast = toast.add({
        title: "Suppression en cours…",
        color: "neutral",
        duration: 0,
        close: false,
        ui: { icon: "animate-spin" },
        icon: "material-symbols:progress-activity",
      });
    }
    try {
      await $fetch("/storage/object", {
        method: "DELETE",
        query: { folder_path: full_path },
      });

      useFileTree().retryFetching();
      if (loadingToast) toast.remove(loadingToast.id);
      if (!options?.silent) {
        toast.add({
          title: "Élément supprimé !",
          color: "success",
          icon: "material-symbols:check-rounded",
        });
      }
    } catch (error: any) {
      if (!options?.silent) {
        if (loadingToast) toast.remove(loadingToast.id);
        toast.add({
          title: "Erreur",
          description:
            error.data?.statusMessage ??
            "Impossible de supprimer le fichier/dossier.",
          color: "error",
          icon: "material-symbols:error-outline-rounded",
        });
      }
      throw error;
    }
  };

  const download = async (
    item: ApiFileItem,
    options?: {
      silent?: boolean;
    },
  ): Promise<void> => {
    const fullPath = item.is_dir
      ? `${joinPath(FSStore.currentPath, item.name)}/`
      : joinPath(FSStore.currentPath, item.name);

    const cleanPath = fullPath.replace(/^\/+/, "");

    let loadingToast: Toast | undefined;

    if (!options?.silent) {
      loadingToast = toast.add({
        title: "Préparation du téléchargement…",
        color: "neutral",
        duration: 0,
        close: false,
        ui: { icon: "animate-spin" },
        icon: "material-symbols:progress-activity",
      });
    }

    try {
      const response = await fetch(`/storage/download/${cleanPath}`);

      if (!response.ok) {
        if (loadingToast) toast.remove(loadingToast.id);
        const text = (await response.json()) as GenericAPIResponse<null>;
        const errorMessage = text.message;
        throw new Error(errorMessage || "Le téléchargement a échoué");
      }

      const contentDisposition = response.headers.get("Content-Disposition");
      const filename =
        contentDisposition?.match(/filename="?([^"]+)"?/i)?.[1] ??
        (item.is_dir ? `${item.name}.zip` : item.name);

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      // Téléchargement
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();

      URL.revokeObjectURL(url);

      // Feedback UNIQUEMENT en mode non-batch
      if (loadingToast) toast.remove(loadingToast.id);

      if (!options?.silent) {
        toast.add({
          title: "Téléchargement lancé",
          color: "success",
          icon: "material-symbols:download-rounded",
        });
      }
    } catch (error: any) {
      if (!options?.silent) {
        if (loadingToast) toast.remove(loadingToast.id);
        toast.add({
          title: "Erreur",
          icon: "material-symbols:error-outline-rounded",
          description: error.message.message || "Le téléchargement a échoué",
          color: "error",
        });
      }
    }
  };

  const upload = async (
    file: File,
    options?: {
      silent?: boolean;
    },
  ): Promise<void> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("path", FSStore.currentPath);

    let loadingToast: Toast | undefined;

    if (!options?.silent) {
      loadingToast = toast.add({
        title: "Upload en cours…",
        description: file.name,
        color: "neutral",
        duration: 0,
        close: false,
        ui: { icon: "animate-spin" },
        icon: "material-symbols:progress-activity",
      });
    }

    try {
      await $fetch<GenericAPIResponse<null>>("/storage/upload", {
        method: "POST",
        body: formData,
      });

      useFileTree().retryFetching();

      if (loadingToast) toast.remove(loadingToast.id);

      if (!options?.silent) {
        toast.add({
          title: "Fichier uploadé",
          description: file.name,
          color: "success",
          icon: "material-symbols:check-rounded",
        });
      }
    } catch (error: any) {
      if (!options?.silent) {
        if (loadingToast) toast.remove(loadingToast.id);
        toast.add({
          title: "Erreur lors de l'upload",
          icon: "material-symbols:error-outline-rounded",
          description:
            error.data?.statusMessage ?? `Impossible d'uploader ${file.name}.`,
          color: "error",
        });
      }
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
    } catch (error: any) {
      const message =
        error.data?.statusMessage || "Impossible de récupérer les stats.";
      toast.add({ title: "Erreur", description: message, color: "error" });
      throw error;
    }
  };

  const terminal = (item: ApiFileItem) => {
    navigateTo("/terminal");
    FSStore.navigate(item.name);
  };

  const copy = async (
    item: ApiFileItem,
  ): Promise<GenericAPIResponse<CopyFilePayload>> => {
    const full_path = item.is_dir
      ? `${joinPath(FSStore.currentPath, item.name)}/`
      : joinPath(FSStore.currentPath, item.name);

    const loadingToast = toast.add({
      title: "Copie en cours...",
      color: "neutral",
      duration: 0,
      close: false,
      ui: {
        icon: "animate-spin",
      },
      icon: "material-symbols:progress-activity",
    });
    try {
      const req = await $fetch<GenericAPIResponse<CopyFilePayload>>(
        "/storage/copy",
        {
          method: "POST",
          body: {
            source_path: full_path,
            destination_folder: FSStore.currentPath,
          },
        },
      );
      toast.remove(loadingToast.id);
      toast.add({
        title: "Fichier copié !",
        color: "success",
        icon: "material-symbols:check-rounded",
      });

      useFileTree().retryFetching();

      return req;
    } catch (error: any) {
      const message =
        error.data?.statusMessage || "Impossible de copier le fichier/dossier.";
      toast.remove(loadingToast.id);
      toast.add({
        title: "Erreur",
        icon: "material-symbols:error-outline-rounded",
        description: message,
        color: "error",
      });
      throw error;
    }
  };

  const compress = async (
    items: ApiFileItem[],
    destination_folder: string = FSStore.currentPath,
    output_base_name: string = "compressed_folder",
  ): Promise<void> => {
    const object_names = items.map((item) =>
      item.is_dir
        ? `${joinPath(FSStore.currentPath, item.name)}/`
        : joinPath(FSStore.currentPath, item.name),
    );
    let loadingToast: Toast | undefined;

    loadingToast = toast.add({
      title: "Compression en cours...",
      color: "neutral",
      duration: 0,
      close: false,
      ui: {
        icon: "animate-spin",
      },
      icon: "material-symbols:progress-activity",
    });
    try {
      const req = await $fetch<GenericAPIResponse<CompressFileResponse>>(
        "/storage/compress",
        {
          method: "POST",
          body: {
            objects: object_names,
            destination_folder,
            output_base_name,
          },
        },
      );
      useFileTree().retryFetching();

      if (loadingToast) toast.remove(loadingToast.id);
      toast.add({
        title: "Compression terminée",
        color: "success",
        icon: "material-symbols:check-rounded",
        description: `Résultat dans ${req.data?.output_object_name}`,
      });
    } catch (error: any) {
      const message =
        error.data?.statusMessage || "Impossible de compresser les fichiers.";
      if (loadingToast) toast.remove(loadingToast.id);
      toast.add({
        title: "Erreur lors de la compression",
        icon: "material-symbols:error-outline-rounded",
        description: message,
        color: "error",
      });
      throw error;
    }
  };

  const createFolder = async (
    folderName: string,
    currentPath: string = FSStore.currentPath,
  ): Promise<{ success: boolean; message?: string }> => {
    try {
      const req = await $fetch<GenericAPIResponse<string>>("/storage/folder", {
        method: "POST",
        body: {
          currentPath,
          folderPath: folderName,
        },
      });
      useFileTree().retryFetching();
      toast.add({
        title: "Dossier créer",
        color: "success",
        icon: "material-symbols:check-rounded",
      });
      return { success: true };
    } catch (error: any) {
      const message =
        error.data?.message ??
        error.data?.detail ??
        `Impossible de créer le dossier "${folderName}".`;

      return { success: false, message };
    }
  };

  const move = async (
    item_name: string,
    destination_folder: string,
    options?: {
      silent?: boolean;
    },
  ) => {
    const payload: MoveFilePayload = {
      source_path: item_name,
      destination_folder: destination_folder,
    };
    let loadingToast: Toast | undefined;
    try {
      loadingToast = toast.add({
        title: "Déplacement en cours...",
        color: "neutral",
        duration: 0,
        close: false,
        ui: { icon: "animate-spin" },
        icon: "material-symbols:progress-activity",
      });

      const req = await $fetch<GenericAPIResponse<CopyFilePayload>>(
        "/storage/move",
        {
          method: "POST",
          body: payload,
        },
      );

      useFileTree().retryFetching();
      if (loadingToast) toast.remove(loadingToast.id);
      return req;
    } catch (error: any) {
      if (loadingToast) toast.remove(loadingToast.id);
      const message =
        error.data?.data.message ||
        "Impossible de renommer le fichier/dossier.";
      toast.add({
        title: "Erreur",
        icon: "material-symbols:error-outline-rounded",
        description: message,
        color: "error",
      });
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
    move,
  };
};
