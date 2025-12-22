<script lang="ts" setup>
import type { ContextMenuItem, TableRow } from "@nuxt/ui";
import { useFileRenameRegistry } from "~/composables/file/RenameRegistry";
import type { ApiFileItem } from "~~/shared/types/file_tree";

const props = defineProps<{
  row: TableRow<ApiFileItem> | null;
}>();

const fsActions = useFsActions();
const FSStore = useFSStore();

const { start } = useFileRenameRegistry();

// Génère les items du context menu selon le type de fichier
function getRowItems(row: TableRow<ApiFileItem>): ContextMenuItem[] {
  if (!row) return [];

  const item = row.original;

  if (item.is_dir) {
    return [
      {
        label: "Ouvrir dans le terminal",
        icon: "material-symbols:terminal-rounded",
        onSelect() {},
      },
      { type: "separator" as const },
      {
        label: "Ouvrir le dossier",
        icon: "material-symbols:folder-open-outline-rounded",
        onSelect() {
          fsActions.open(item);
        },
      },
      {
        label: "Renommer",
        icon: "material-symbols:edit-outline-rounded",
        onSelect() {
          if (props.row) {
            const key = joinPath(FSStore.currentPath, props.row.original.name);
            start(key);
          }
        },
      },
      {
        label: "Supprimer",
        icon: "material-symbols:delete-outline-rounded",
        color: "error" as const,
        onSelect() {},
      },
      { type: "separator" as const },
      {
        label: "Propriétés",
        icon: "material-symbols:info-outline-rounded",
        onSelect() {},
      },
    ];
  } else {
    return [
      {
        label: "Visualiser",
        icon: "material-symbols:visibility-outline-rounded",
        onSelect() {},
      },
      { type: "separator" as const },
      {
        label: "Télécharger",
        icon: "material-symbols:download-rounded",
        onSelect() {},
      },
      {
        label: "Renommer",
        icon: "material-symbols:edit-outline-rounded",
        onSelect() {
          if (props.row) {
            const key = joinPath(FSStore.currentPath, props.row.original.name);
            start(key);
          }
        },
      },
      {
        label: "Supprimer",
        icon: "material-symbols:delete-outline-rounded",
        color: "error" as const,
        onSelect() {},
      },
      { type: "separator" as const },
      {
        label: "Propriétés",
        icon: "material-symbols:info-outline-rounded",
        onSelect() {},
      },
    ];
  }
}
</script>

<template>
  <UContextMenu :items="row ? getRowItems(row) : []" :aria-hidden="false">
    <slot />
  </UContextMenu>
</template>
