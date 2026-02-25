<script lang="ts" setup>
import { LazyFileExplorerModalCreateFolder } from "#components";

const overlay = useOverlay();

const createFolderModal = overlay.create(LazyFileExplorerModalCreateFolder);

async function openModal() {
  const modal = createFolderModal.open();

  const result = await modal.result;
}
</script>

<template>
  <LazyUTooltip text="Create folder" :delay-duration="0">
    <UButton
      :square="true"
      icon="material-symbols:create-new-folder-outline"
      color="neutral"
      variant="outline"
      size="lg"
      class="shadow-md"
      @click="openModal"
    />
  </LazyUTooltip>
</template>
