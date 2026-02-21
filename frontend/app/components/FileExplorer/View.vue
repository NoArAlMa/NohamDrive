<script lang="ts" setup>
const props = defineProps<{
  fileUrl: File;
  fileName: string;
}>();
</script>

<template>
  <UModal
    dismissible
    fullscreen
    title="Prévisualisation du fichier"
    :description="props.fileName"
    :ui="{
      content: 'flex flex-col h-screen',
      body: 'flex-1 min-h-0 p-0',
    }"
  >
    <template #body>
      <div class="w-full h-full overflow-hidden">
        <ClientOnly>
          <div
            class="w-full h-full max-w-full max-h-full flex items-center justify-center"
          >
            <VueFilesPreview :file="props.fileUrl" class="w-full h-full" />
          </div>
        </ClientOnly>
      </div>
    </template>
  </UModal>
</template>

<style scoped>
:deep(canvas),
:deep(iframe),
:deep(embed) {
  width: 100% !important;
  height: 100vh !important;
  max-width: 100% !important;
  max-height: 100% !important;
  object-fit: contain;
}

:deep(audio) {
  width: 100% !important;
  max-width: 100% !important;
}

:deep(video) {
  max-width: 100% !important;
  max-height: 100% !important;
}

:deep(.md-preview) {
  display: flex;
  justify-content: center;
  padding: 2rem;
  width: 100%;
  overflow-y: auto;
}

:deep(.md-preview table) {
  width: 100%;

  margin: 1rem 0;
  border-radius: 0.25rem;
  font-size: 0.95rem;
  border: 1px solid rgb(55 65 81);
  border-radius: 8px;
  overflow: hidden;
}

:deep(.md-preview hr) {
  margin-top: 5px;
  margin-bottom: 5px;
}

/* Header */
:deep(.md-preview thead) {
  background-color: rgb(31 41 55);
}

:deep(.md-preview th) {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  border-bottom: 1px solid rgb(55 65 81);
}

/* Cellules */
:deep(.md-preview td) {
  padding: 0.75rem 1rem;
  border-top: 1px solid rgb(55 65 81);
}

:deep(.md-preview tbody tr:nth-child(even)) {
  background-color: rgb(55 65 81);
}

/* Hover */
:deep(.md-preview tbody tr:hover) {
  background-color: rgb(55 65 81 / 0.3);
  transition: background 0.2s ease;
}
</style>
