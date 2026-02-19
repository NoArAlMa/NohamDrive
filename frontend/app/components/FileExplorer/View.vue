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
</style>
