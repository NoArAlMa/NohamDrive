<script lang="ts" setup>
import { LazyFileExplorerModalCreateFolder } from "#components";
import type { DropdownMenuItem } from "@nuxt/ui";

const { t } = useI18n();

const overlay = useOverlay();
const { runBatch } = useBatchAction();
const { upload } = useFsActions();

const createFolderModal = overlay.create(LazyFileExplorerModalCreateFolder);

async function openModal() {
  const modal = createFolderModal.open();
  const result = await modal.result;
}

const items = computed<DropdownMenuItem[]>(() => [
  {
    label: t("fileExplorer.createFolder") as string,
    icon: "material-symbols:create-new-folder-outline-rounded",
    onSelect: () => {
      openModal();
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
        await runBatch(files, upload, {
          loading: t("fileExplorer.uploading") as string,
          success: t("fileExplorer.uploadSuccess") as string,
          error: t("fileExplorer.uploadError") as string,
        });
      } else {
        await upload(files[0]!);
      }
    },
  },
]);
</script>

<template>
  <LazyUTooltip :text="String(t('fileExplorer.add'))" :delay-duration="0">
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
        class="shadow-sm"
      />
    </UDropdownMenu>
  </LazyUTooltip>
</template>
