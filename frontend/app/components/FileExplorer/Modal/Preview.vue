<script lang="ts" setup>
const { fileName, file } = defineProps<{
  file: File | null;
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
            <VueFilesPreview :file="file" class="w-full h-full" />
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

:deep(img) {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 0.5rem;
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

/* AUDIO WRAPPER */
:deep(.audio-preview) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
}

/* CARD */
:deep(.audio-container) {
  display: flex;
  align-items: center;
  gap: 1.25rem;

  width: 100%;
  max-width: 720px;

  padding: 1.25rem 1.5rem;

  border-radius: 0.5rem;
  background: var(--ui-bg-elevated);
  border: 1px solid var(--ui-border);

  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);

  transition: all 0.2s ease;
}

/* FILE NAME */
:deep(.audio-container > .flex-column > div) {
  font-size: 0.95rem !important;
  font-weight: 500;
  color: var(--ui-text) !important;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* AUDIO PLAYER */
:deep(audio) {
  width: 240px;
  height: 36px;
  border-radius: 0.5rem;
}

/* MODE BUTTON */
:deep(.mode-btn) {
  background: var(--ui-secondary);
  border: 1px solid var(--ui-border-muted);
  color: var(--ui-text);

  padding: 0.4rem 0.9rem;
  border-radius: 0.5rem;

  font-size: 0.85rem;
  font-weight: 500;

  transition: all 0.15s ease;
}

/* VISUALIZER */
:deep(.cvs-container) {
  width: 100%;
  max-width: 720px;

  border-radius: 0.5rem;
  overflow: hidden;

  background: var(--ui-bg-elevated);
  border: 1px solid var(--ui-border);
}

/* Canvas */
:deep(canvas) {
  width: 100% !important;
  height: 150px !important;
  border-radius: 12px;
}
</style>
