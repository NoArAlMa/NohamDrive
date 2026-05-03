<script lang="ts" setup>
import { VueFilesPreview } from "vue-files-preview";

const props = defineProps<{
  file?: File;
  fileName: string;
  previewPath?: string;
}>();

const showPreview = ref(true);
const file = shallowRef<File | null>(props.file ?? null);
const loading = ref(!props.file);
const errorMessage = ref<string | null>(null);
const previewKey = ref(0);
let abortController: AbortController | null = null;

const previewUrl = computed(() =>
  props.previewPath ? `api/storage/preview/${props.previewPath}` : null,
);

async function fetchPreview() {
  if (file.value || !previewUrl.value) {
    loading.value = false;
    return;
  }

  abortController?.abort();
  abortController = new AbortController();

  try {
    loading.value = true;
    errorMessage.value = null;

    const response = await $fetch<Blob>(previewUrl.value, {
      responseType: "blob",
      signal: abortController.signal,
    });

    const blob = new Blob([response], { type: response.type });
    file.value = new File([blob], props.fileName, { type: blob.type });
    previewKey.value++;
  } catch (error: any) {
    if (error?.name === "AbortError") return;
    errorMessage.value =
      error?.data?.statusMessage ??
      error?.statusMessage ??
      "Impossible de prévisualiser ce fichier.";
  } finally {
    loading.value = false;
  }
}

function closeModal() {
  abortController?.abort();
  showPreview.value = false;
}

onMounted(() => {
  void fetchPreview();
});

onBeforeUnmount(() => {
  abortController?.abort();
});
</script>

<template>
  <LazyUModal
    dismissible
    fullscreen
    title="Prévisualisation du fichier"
    :description="fileName"
    :close="{
      onClick: () => {
        closeModal();
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
            <div
              v-if="loading"
              class="flex flex-col items-center justify-center gap-3 text-muted"
            >
              <UIcon
                name="material-symbols:progress-activity"
                class="size-8 animate-spin"
              />
              <span class="text-sm">Chargement de la prévisualisation...</span>
            </div>
            <UAlert
              v-else-if="errorMessage"
              color="error"
              icon="material-symbols:error-outline-rounded"
              title="Erreur"
              :description="errorMessage"
              class="max-w-lg"
            />
            <VueFilesPreview
              v-else-if="showPreview && file"
              :key="previewKey"
              :file="file"
              v-bind="$attrs"
              class="w-full h-full"
            />
          </div>
        </ClientOnly>
      </div>
    </template>
  </LazyUModal>
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
