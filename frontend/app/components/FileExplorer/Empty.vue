<script lang="ts" setup>
import { LazyFileExplorerModalCreateFolder } from "#components";

const overlay = useOverlay();
const createFolderModal = overlay.create(LazyFileExplorerModalCreateFolder);

async function openCreateFolderModal() {
  const modal = createFolderModal.open();
  const result = await modal.result;
}

function goBack() {
  const fs = useFSStore();
  fs.navigate("..");
}
</script>

<template>
  <LazyUEmpty
    class="w-full tablet:w-fit min-w-125"
    variant="soft"
    icon="material-symbols:sad-tab-outline-rounded"
    title="No files"
    description="It looks like you haven't added any files/folders. Create one to get started."
    size="xl"
    :actions="[
      {
        icon: 'material-symbols:keyboard-return-rounded',
        label: 'Return',
        color: 'neutral',
        variant: 'soft',
        size: 'md',
        loadingAuto: true,
        onClick: goBack,
      },
      {
        icon: 'material-symbols:create-new-folder-outline-rounded',
        label: 'Create Folder',
        color: 'primary',
        variant: 'subtle',
        size: 'md',
        loadingAuto: true,
        onClick: openCreateFolderModal,
      },
    ]"
  />
</template>
