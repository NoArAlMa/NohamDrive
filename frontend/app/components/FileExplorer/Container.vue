<script setup lang="ts">
const FileCount = ref(0);
const selectedItems = ref<ApiFileItem[]>([]);

const isDragging = ref(false); // Affiche l'overlay de drag
const dragCounter = ref(0); // Compteur pour gérer les entrées/sorties de la zone de drop

const { upload } = useFsActions();

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

  // Récupère tous les fichiers déposés
  const files = Array.from(e.dataTransfer?.files || []);
  if (files.length > 0) {
    console.log(files);
    await upload(files);
  }
}
</script>

<template>
  <section
    class="flex flex-col h-full w-full overflow-hidden relative rounded-xl"
  >
    <div class="shrink-0 p-2 border-b flex items-center justify-between">
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
    >
      <!-- Overlay -->
      <Transition name="drop-fade">
        <div
          v-if="isDragging"
          class="absolute inset-0 z-50 flex flex-col gap-3 items-center justify-center backdrop-blur-sm rounded-md border-2 border-white border-dashed bg-black/10 pointer-events-none"
        >
          <!-- Icône -->
          <UIcon
            name="material-symbols:file-copy-outline-rounded"
            class="size-10"
          />
          <p class="text-2xl font-semibold">Drop your file here</p>
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
