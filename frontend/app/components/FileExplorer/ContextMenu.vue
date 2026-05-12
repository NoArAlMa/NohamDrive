<script lang="ts" setup>
import type { ContextMenuItem, TableRow } from "@nuxt/ui";
import { useFileRenameRegistry } from "~/composables/file/RenameRegistry";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import { LazyFileExplorerModalCreateFolder } from "#components";

const { t } = useI18n();

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
    label: t("fileExplorer.download") as string,
    icon: "material-symbols:download-rounded",
    onSelect: () => fsActions.download(item),
  },
  {
    label: t("fileExplorer.duplicate") as string,
    icon: "material-symbols:content-copy-outline-rounded",
    onSelect: () => fsActions.copy(item),
  },
  {
    label: t("fileExplorer.rename") as string,
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
    label: t("fileExplorer.delete") as string,
    icon: "material-symbols:delete-outline-rounded",
    color: "error" as const,
    onSelect: () => fsActions.del(item),
  },
  {
    label: t("fileExplorer.properties") as string,
    icon: "material-symbols:info-outline-rounded",
    onSelect: () => fsActions.property(item),
  },
];

// Menu complet avec ajout spécifique
const rowItems = computed((): ContextMenuItem[] => {
  if (!props.row)
    return [
      {
        label: t("fileExplorer.createFolder") as string,
        icon: "material-symbols:create-new-folder-outline-rounded",
        onSelect: () => {
          const createFolderModal = overlay.create(
            LazyFileExplorerModalCreateFolder,
          );

          createFolderModal.open();
        },
      },
      {
        label: t("fileExplorer.importFile") as string,
        icon: "material-symbols:file-open-outline-rounded",
        onSelect: async () => {
  
          const files = await openFilePicker(true);


          if (!files.length) {
            return;
          }

          if (files.length > 1) {
            await runBatch(files, fsActions.upload, {
              loading: t("fileExplorer.uploading") as string,
              success: t("fileExplorer.uploadSuccess") as string,
              error: t("fileExplorer.uploadError") as string,
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
        label: t("fileExplorer.openWithEcho") as string,
        icon: "terminal:echo-icon",
        onSelect: () => fsActions.terminal(item),
      },
      { type: "separator" as const },
      ...baseMenu(item),
    ];
  } else {
    return [
      {
        label: t("fileExplorer.preview") as string,
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
