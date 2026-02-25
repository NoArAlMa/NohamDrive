<script lang="ts" setup>
import type { ContextMenuItem, TableRow } from "@nuxt/ui";
import { useFileRenameRegistry } from "~/composables/file/RenameRegistry";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import { LazyFileExplorerModalCreateFolder } from "#components";

const props = defineProps<{
  row: TableRow<ApiFileItem> | ApiFileItem | null;
}>();

const overlay = useOverlay();
const fsActions = useFsActions();
const FSStore = useFSStore();
const { runBatch } = useBatchAction();

const { start } = useFileRenameRegistry();

const baseMenu = (item: ApiFileItem): ContextMenuItem[] => [
  {
    label: "Télécharger",
    icon: "material-symbols:download-rounded",
    onSelect: () => fsActions.download(item),
  },
  {
    label: "Dupliquer",
    icon: "material-symbols:content-copy-outline-rounded",
    onSelect: () => fsActions.copy(item),
  },
  {
    label: "Renommer",
    icon: "material-symbols:edit-outline-rounded",
    onSelect: () => {
      if (props.row) {
        const key = joinPath(FSStore.currentPath, item.name);
        start(key);
      }
    },
  },
  { type: "separator" as const },
  {
    label: "Supprimer",
    icon: "material-symbols:delete-outline-rounded",
    color: "error" as const,
    onSelect: () => fsActions.del(item),
  },
  {
    label: "Propriétés",
    icon: "material-symbols:info-outline-rounded",
    onSelect: () => fsActions.property(item),
  },
];

// Menu complet avec ajout spécifique
const rowItems = computed((): ContextMenuItem[] => {
  if (!props.row)
    return [
      {
        label: "Creer dossier",
        icon: "material-symbols:create-new-folder-outline-rounded",
        onSelect: () => {
          const createFolderModal = overlay.create(
            LazyFileExplorerModalCreateFolder,
          );

          createFolderModal.open();
        },
      },
      {
        label: "Import file",
        icon: "material-symbols:file-open-outline-rounded",
        onSelect: async () => {
          console.log("Début de la sélection de fichiers...");
          const files = await openFilePicker(true);
          console.log("Fichiers sélectionnés :", files);

          if (!files.length) {
            console.log("Aucun fichier sélectionné.");
            return;
          }

          if (files.length > 1) {
            await runBatch(files, fsActions.upload, {
              loading: "Upload en cours…",
              success: "Upload terminé",
              error: "Une erreur est survenue pendant l’upload.",
            });
          } else {
            await fsActions.upload(files[0]!);
          }
        },
      },
    ];
  const item: ApiFileItem =
    "original" in props.row ? props.row.original : props.row;
  if (item.is_dir) {
    return [
      {
        label: "Ouvrir avec Echo",
        icon: "mdi:star-four-points-outline",
        onSelect: () => fsActions.terminal(item),
      },
      { type: "separator" as const },
      ...baseMenu(item),
    ];
  } else {
    return [
      {
        label: "Visualiser",
        icon: "material-symbols:visibility-outline-rounded",
        onSelect: () => {
          fsActions.open(item);
        },
      },
      { type: "separator" as const },
      ...baseMenu(item),
    ];
  }
});
</script>

<template>
  <LazyUContextMenu :items="rowItems">
    <slot />
  </LazyUContextMenu>
</template>
