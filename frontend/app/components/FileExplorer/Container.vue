<script setup lang="ts">
import {
  LazyFileExplorerHeaderBreadcrumb,
  LazyFileExplorerHeaderSelectColumns,
  LazyFileExplorerHeaderSelectDisplay,
  LazyFileExplorerHeaderToolbar,
  LazyFileExplorerHeaderUpload,
} from "#components";

const FileCount = ref(0);
const selectedItems = ref<ApiFileItem[]>([]);
const explorerRef = ref();
const isDragging = ref(false);
const dragCounter = ref(0);

const { upload } = useFsActions();
const { runBatch } = useBatchAction();
const { isMobile } = useResponsive();
const { viewMode } = useFileExplorerSettings();
const isList = computed(() => viewMode.value === "list");

// Fonction pour gérer l'entrée dans la zone de drop
function onDragEnter(e: DragEvent) {
  const hasFiles = e.dataTransfer?.types.includes("Files");

  if (!hasFiles) return;

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
  const hasFiles = e.dataTransfer?.types.includes("Files");
  if (!hasFiles) return;

  e.preventDefault();
}
// Fonction pour gérer le drop des fichiers
async function onDrop(e: DragEvent) {
  const hasFiles = e.dataTransfer?.files?.length;
  if (!hasFiles) return;

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
  } else {
    await upload(files[0]!);
  }
}

async function clearSelectionedFiles(explorerRef: any) {
  await explorerRef?.clearSelection();
}
</script>

<template>
  <section
    class="flex flex-col relative rounded-md laptop:border border-muted px-0 py-0 laptop:px-2 laptop:py-2"
  >
    <div class="shrink-0 pl-1 pr-1 mb-1 flex items-center justify-between h-12">
      <div class="rounded-md px-2 py-1.5 md:border border-muted shadow-md">
        <div v-if="FileCount > 0" class="flex gap-1 items-center">
          <LazyFileExplorerHeaderToolbar :items="selectedItems" />
          <USeparator
            :decorative="true"
            orientation="vertical"
            class="h-6 mr-2"
          />
          <UTooltip text="Unselect all" :delay-duration="200">
            <UButton
              variant="subtle"
              size="sm"
              color="error"
              leading-icon="material-symbols:close"
              @click="clearSelectionedFiles(explorerRef)"
            />
          </UTooltip>
        </div>
        <LazyFileExplorerHeaderBreadcrumb v-else />
      </div>

      <div class="flex flex-row gap-2 shrink-0" v-if="!isMobile">
        <LazyFileExplorerHeaderSelectDisplay />
        <LazyFileExplorerHeaderSelectColumns v-if="isList" />
        <LazyFileExplorerHeaderUpload />
      </div>
    </div>

    <div
      class="flex-1 relative overflow-hidden"
      @dragenter="onDragEnter"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <!-- Overlay -->
      <Transition name="drop-fade">
        <div
          v-if="isDragging"
          class="absolute inset-0 z-50 flex flex-col gap-3 items-center justify-center backdrop-blur-sm rounded-md border-2 border-white border-dashed bg-black/10 pointer-events-none"
        >
          <LazyUIcon
            name="material-symbols:file-copy-outline-rounded"
            class="size-10"
          />
          <p class="text-2xl font-semibold">Drop your file(s) here</p>
        </div>
      </Transition>
      <ClientOnly>
        <LazyFileExplorerViewList
          v-if="viewMode === 'list' || isMobile"
          v-model:selectedCount="FileCount"
          v-model:selected-items="selectedItems"
          ref="explorerRef"
        />
        <LazyFileExplorerViewTiles
          v-else-if="viewMode === 'tiles' && !isMobile"
          v-model:selectedCount="FileCount"
          v-model:selected-items="selectedItems"
          ref="explorerRef"
        />
      </ClientOnly>
    </div>

    <LazyFileExplorerFooter :selected-count="FileCount" />
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
