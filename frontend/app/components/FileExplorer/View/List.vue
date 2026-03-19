<script lang="ts" setup>
import type { TableRow } from "@nuxt/ui";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import { UCheckbox, UButton, UDropdownMenu, UIcon } from "#components";
import type { Row } from "@tanstack/vue-table";
const ExplorerContextMenu = defineAsyncComponent(
  () => import("../ContextMenu.vue"),
);
const ExplorerError = defineAsyncComponent(() => import("../Error.vue"));
const ExplorerLoader = defineAsyncComponent(() => import("../Loader/List.vue"));

const fileTreeStore = useFileTree();
const { fileTree, loading, hasError, errorMessage, errorStatus } =
  storeToRefs(fileTreeStore);

// Variable "debounced" du loading
const loading_debounced = refDebounced(loading, 100);

const selection = useFileExplorerSelection();
const { viewMode } = useFileExplorerSettings();
const { isMobile } = useResponsive();

const rowSelection = ref<Record<string, boolean>>({});
const sorting = ref([]);

const contextRow = ref<TableRow<ApiFileItem> | null>(null);
const contextOpen = ref(false);

const table = useTemplateRef("table");

function handleOpenChange(v: boolean) {
  if (!v) {
    setTimeout(() => {
      contextRow.value = null;
    }, 80);
  }
}

watch(
  rowSelection,
  (rows) => {
    const items = Object.keys(rows)
      .filter((k) => rows[k])
      .map((index) => fileTree.value[Number(index)])
      .filter((item): item is ApiFileItem => item !== undefined);

    selection.set(items);
  },
  { deep: true },
);

const { columns } = useFileExplorerColumns(
  {
    UCheckbox,
    UButton,
    UDropdownMenu,
    UIcon,
  },
  isMobile,
);

function clearSelection() {
  rowSelection.value = {};
  selection.clear();
  contextRow.value = null;
}

watch(fileTree, () => {
  clearSelection();
});

defineExpose({
  clearSelection,
});
</script>

<template>
  <ExplorerContextMenu
    :row="contextRow"
    v-model:open="contextOpen"
    @update:open="handleOpenChange"
  >
    <div class="h-full w-full overflow-y-hidden overflow-x-hidden">
      <LazyUTable
        ref="table"
        v-model:sorting="sorting"
        v-model:row-selection="rowSelection"
        :loading="loading_debounced"
        loading-color="info"
        :sticky="true"
        :data="fileTree"
        :columns="columns"
        :ui="{
          tbody: 'file-explorer-tbody',
          td: viewMode === 'list' ? ['py-1'] : ['py-0'],
        }"
        :virtualize="false"
        @hover=""
        :meta="{
          class: 'text-center',
        }"
        class="w-full h-full overflow-x-hidden table-fixed"
        @contextmenu="
          (e: MouseEvent, row: Row<ApiFileItem>) => {
            if (isMobile) {
              return;
            }
            contextRow = row ?? null;
            contextOpen = true;
          }
        "
      >
        <template #name-cell="{ row }">
          <LazyFileExplorerElementsRow :row="row" />
        </template>

        <!-- Page lorsque l'explorateur est vide  -->
        <template #empty>
          <div v-if="!hasError" class="flex items-center justify-center">
            <FileExplorerEmpty />
          </div>

          <ExplorerError
            v-if="hasError"
            :ErrorStatus="errorStatus"
            :message="errorMessage"
            :on-retry="useFileTree().retryFetching"
          />
        </template>
        <!-- Page pour le chargement de l'explorateur -->
        <template #loading>
          <ExplorerLoader v-if="loading_debounced" />
        </template>
      </LazyUTable>
    </div>
  </ExplorerContextMenu>
</template>
