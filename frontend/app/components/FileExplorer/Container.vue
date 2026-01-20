<script setup lang="ts">
const FileCount = ref(0);
const selectedItems = ref<ApiFileItem[]>([]);

const isDragging = ref(false); // Affiche l'overlay de drag
const dragCounter = ref(0); // Compteur pour gérer les entrées/sorties de la zone de drop

const { upload } = useFsActions();
const { runBatch } = useBatchAction();

// Fonction pour gérer l'entrée dans la zone de drop
function onDragEnter(e: DragEvent) {
  e.preventDefault();
  dragCounter.value++;
  isDragging.value = true;
}

// Fonction pour gérer la sortie de la zone de drop
function onDragLeave(e: DragEvent) {
  e.preventDefault();
  dragCounter.value--;
  if (dragCounter.value === 0) {
    isDragging.value = false;
  }
}

// Fonction pour empêcher le comportement par défaut pendant le drag
function onDragOver(e: DragEvent) {
  e.preventDefault();
}

// Fonction pour gérer le drop des fichiers
async function onDrop(e: DragEvent) {
  e.preventDefault();
  dragCounter.value = 0;
  isDragging.value = false;

  const files = Array.from(e.dataTransfer?.files || []);
  if (!files.length) return;
  if (files.length > 1) {
    await runBatch(files, upload, {
      loading: "Upload en cours…",
      success: "Upload terminé",
      error: "Une erreur est survenue pendant l’upload.",
    });
  } else if (files[0]) {
    await upload(files[0]);
  }
}
</script>

<template>
  <section
    class="flex flex-col h-full w-full overflow-hidden relative rounded-xl px-5 py-3 bg-[#0D1520] border border-muted shadow-lg"
  >
    <div class="shrink-0 p-2 border-b flex items-center justify-between h-12">
      <div>
        <FileExplorerToolbar :items="selectedItems" v-if="FileCount > 0" />
        <FileExplorerBreadcrumb v-else />
      </div>
      <div>
        <FileExplorerUploadFolder />
      </div>
    </div>

    <div
      class="flex-1 relative overflow-hidden"
      @dragenter="onDragEnter"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
      role="region"
      aria-label="File upload dropzone"
      tabindex="0"
    >
      <!-- Overlay -->
      <Transition name="drop-fade">
        <div
          v-if="isDragging"
          class="absolute inset-0 z-50 flex flex-col gap-3 items-center justify-center backdrop-blur-sm rounded-md border-2 border-white border-dashed bg-black/10 pointer-events-none"
        >
          <UIcon
            name="material-symbols:file-copy-outline-rounded"
            class="size-10"
          />
          <p class="text-2xl font-semibold">Drop your file(s) here</p>
        </div>
      </Transition>
      <ClientOnly>
        <FileExplorer
          v-model:selectedCount="FileCount"
          v-model:selected-items="selectedItems"
        />
      </ClientOnly>
    </div>

    <FileExplorerFooter :selected-count="FileCount" />
  </section>
</template>

<style scoped>
.drop-fade-enter-active,
.drop-fade-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.drop-fade-enter-from,
.drop-fade-leave-to {
  opacity: 0;
  transform: scale(0.98);
}
</style>
