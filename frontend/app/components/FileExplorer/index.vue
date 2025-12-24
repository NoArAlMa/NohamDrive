<script lang="ts" setup>
import type { TableRow } from "@nuxt/ui";
import { resolveComponent } from "vue";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import ExplorerContextMenu from "./ExplorerContextMenu.vue";
import FileBreadcrumb from "./Breadcrumb.vue";
import ExplorerError from "./ExplorerError.vue";
import ExplorerLoader from "./ExplorerLoader.vue";
import { useDropZone } from "@vueuse/core";
import { useTemplateRef } from "vue";

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

const loading_debounced = refDebounced(loading, 100);

// --- DRAG & DROP NATIF ---
const isDragging = ref(false);
const dragCounter = ref(0);
const dropZoneRef = ref<HTMLElement | null>(null);

function onDrop(files: File[] | null) {
  if (!files || files.length === 0) return;

  dragCounter.value = 0;
  isDragging.value = false;

  useFsActions().upload(files);
}
</script>

<template>
  <ExplorerContextMenu :row="contextRow">
    <UTable
      v-model:sorting="sorting"
      :loading="loading"
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
  </ExplorerContextMenu>
</template>
