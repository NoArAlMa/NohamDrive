<script lang="ts" setup>
const { fileName, fileUrl } = defineProps<{
  fileUrl: File | null;
  fileName: string;
}>();

const showPreview = ref(true);

function closeModal() {
  showPreview.value = false;
}
</script>

<template>
  <UModal
    dismissible
    fullscreen
    title="Prévisualisation du fichier"
    :description="fileName"
    :close="{
      onClick: () => {
        closeModal;
      },
    }"
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
            <VueFilesPreview :file="fileUrl" class="w-full h-full" />
          </div>
        </ClientOnly>
      </div>
    </template>
  </UModal>
</template>

<style scoped>
:deep(iframe),
:deep(embed) {
  width: 100% !important;
  height: 100vh !important;
  max-width: 100% !important;
  max-height: 100% !important;
  object-fit: contain;
}

/* VIDEO */

:deep(video) {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  max-height: 80vh;
  border-radius: 12px;
}
:deep(video:fullscreen) {
  border-radius: 0;
}

/* MARKDOWN */

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

:deep(.md-preview thead) {
  background-color: rgb(31 41 55);
}

:deep(.md-preview th) {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  border-bottom: 1px solid rgb(55 65 81);
}

:deep(.md-preview td) {
  padding: 0.75rem 1rem;
  border-top: 1px solid rgb(55 65 81);
}

:deep(.md-preview tbody tr:nth-child(even)) {
  background-color: rgb(55 65 81);
}

:deep(.md-preview tbody tr:hover) {
  background-color: rgb(55 65 81 / 0.3);
  transition: background 0.2s ease;
}

/* AUDIO */

:deep(.audio-preview) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 2rem;
}

/* Carte audio */
:deep(.audio-container) {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  max-width: 900px;
  width: 100%;
}

/* Nom du fichier */
:deep(.audio-container > .flex-column > div) {
  font-size: 1.2rem !important;
  font-weight: 600;
  color: var(--ui-text, #e5e5e5) !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Player audio */
:deep(audio) {
  border-radius: 8px;
  width: 280px;
}

/* Bouton mode */
:deep(.mode-btn) {
  background: rgba(255, 255, 255, 0.08);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
}

:deep(.mode-btn:hover) {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

/* Visualizer container */
:deep(.cvs-container) {
  width: 100%;
  max-width: 1000px;
  border-radius: 12px;
  overflow: hidden;
}

/* Canvas */
:deep(canvas) {
  width: 100% !important;
  height: 150px !important;
  border-radius: 12px;
}
</style>
