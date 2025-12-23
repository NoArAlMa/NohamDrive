<script lang="ts" setup>
import type { TableRow } from "@nuxt/ui";
import { resolveComponent } from "vue";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import ExplorerContextMenu from "./ExplorerContextMenu.vue";
import FileBreadcrumb from "./Breadcrumb.vue";
import ExplorerError from "./ExplorerError.vue";
import ExplorerLoader from "./ExplorerLoader.vue";

const { fileTree, hasError, errorMessage, errorStatus, loading } =
  useFileTree();

// Importation des components Nuxt UI pour pouvoir les utiliser en JS
const contextRow = ref<TableRow<ApiFileItem> | null>(null);

const ui = {
  Checkbox: resolveComponent("UCheckbox"),
  Button: resolveComponent("UButton"),
  DropdownMenu: resolveComponent("UDropdownMenu"),
  Icon: resolveComponent("UIcon"),
};

// Importation des colonnes et du système de sorting
const { columns } = useFileExplorerColumns(ui);
const sorting = ref([]);

// Variable "debounced" du loading

const loading_debounced = refDebounced(loading, 500);

// --- DRAG & DROP NATIF ---
const isDragging = ref(false);
const dragCounter = ref(0);

function onDragEnter(e: DragEvent) {
  e.preventDefault();
  dragCounter.value++;
  isDragging.value = true;
}

function onDragLeave(e: DragEvent) {
  e.preventDefault();
  dragCounter.value--;

  if (dragCounter.value === 0) {
    isDragging.value = false;
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault();
}

function onDrop(e: DragEvent) {
  e.preventDefault();
  dragCounter.value = 0;
  isDragging.value = false;

  const files = Array.from(e.dataTransfer?.files ?? []);

  if (files.length === 0) return;

  console.log("📦 Fichiers droppés :", files);

  // MOCK UPLOAD
  useFsActions().upload(files);

  setTimeout(() => {
    console.log("✅ Upload terminé (mock)");
  }, 1000);
}
</script>

<template>
  <ExplorerContextMenu :row="contextRow">
    <div
      class="relative"
      @dragenter="onDragEnter"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <div
        v-show="isDragging"
        class="absolute inset-0 z-50 flex flex-col gap-3 items-center justify-center bg-gray-900/60 border-2 rounded-md border-dashed pointer-events-none"
      >
        <UIcon name="material-symbols:file-copy-outline" class="size-10" />
        <p class="text-xl font-bold">Drop your file here</p>
      </div>
      <UTable
        v-model:sorting="sorting"
        :loading="false"
        loading-color="info"
        :sticky="true"
        :data="fileTree"
        :columns="columns"
        :ui="{
          tbody: 'file-explorer-tbody',
        }"
        @hover=""
        @contextmenu="(e, row) => (contextRow = row)"
      >
        <template #name-cell="{ row }">
          <FileExplorerTableRowFile :row="row" />
        </template>

        <!-- Page lorsque l'explorateur est vide  -->
        <template #empty>
          <div
            v-if="!loading && !hasError && fileTree.length === 0"
            class="flex items-center justify-center"
          >
            <UEmpty
              class="min-w-[500px]"
              variant="soft"
              icon="material-symbols:sad-tab-outline-rounded"
              title="No files"
              description="It looks like you haven't added any files/folders. Create one to get started."
              size="xl"
            />
          </div>

          <ExplorerError
            v-if="hasError"
            :ErrorStatus="errorStatus"
            :message="errorMessage"
          />
        </template>
        <!-- Page pour le chargement de l'explorateur -->
        <template #loading>
          <ExplorerLoader v-if="loading_debounced" />
        </template>
      </UTable>
    </div>
  </ExplorerContextMenu>
</template>
