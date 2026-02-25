<script lang="ts" setup>
import { LazyFileExplorerModalCreateFolder } from "#components";
import type { DropdownMenuItem } from "@nuxt/ui";

const overlay = useOverlay();
const { runBatch } = useBatchAction();
const { upload } = useFsActions();

const createFolderModal = overlay.create(LazyFileExplorerModalCreateFolder);

async function openModal() {
  const modal = createFolderModal.open();
  const result = await modal.result;
}

const items = ref<DropdownMenuItem[]>([
  {
    label: "Creer dossier",
    icon: "material-symbols:create-new-folder-outline-rounded",
    onSelect: () => {
      openModal();
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
        await runBatch(files, upload, {
          loading: "Upload en cours…",
          success: "Upload terminé",
          error: "Une erreur est survenue pendant l’upload.",
        });
      } else {
        await upload(files[0]!);
      }
    },
  },
]);
</script>

<template>
  <LazyUTooltip text="Add" :delay-duration="0">
    <UDropdownMenu
      :arrow="true"
      :content="{ align: 'end', side: 'bottom', sideOffset: 8 }"
      :items="items"
    >
      <UButton
        :square="true"
        icon="material-symbols:add-2-rounded"
        color="primary"
        variant="outline"
        size="lg"
        class="shadow-md"
      />
    </UDropdownMenu>
  </LazyUTooltip>
</template>
