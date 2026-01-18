<script lang="ts" setup>
import type { TableRow } from "@nuxt/ui";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import { UCheckbox, UButton, UDropdownMenu, UIcon } from "#components";

const {
  fileTree,
  hasError,
  errorMessage,
  errorStatus,
  loading,
  retryFetching,
} = useFileTree();

const table = useTemplateRef("table");
const rowSelection = ref<Record<string, boolean>>({});

const emit = defineEmits<{
  (e: "update:selectedCount", count: number): void;
  (e: "update:selectedItems", items: ApiFileItem[]): void;
}>();

const selectedCount = computed({
  get: () => Object.values(rowSelection.value).filter(Boolean).length,
  set: (value) => emit("update:selectedCount", value),
});

const selectedItems = computed<ApiFileItem[]>(() => {
  if (!table.value) return [];

  return (
    table.value.tableApi
      .getSelectedRowModel()
      ?.rows.map((row) => row.original) ?? []
  );
});

watch(selectedItems, (items) => {
  emit("update:selectedItems", items);
});

watch(selectedCount, (count) => emit("update:selectedCount", count), {
  immediate: true,
});

const ExplorerContextMenu = defineAsyncComponent(
  () => import("./ExplorerContextMenu.vue")
);
const ExplorerError = defineAsyncComponent(() => import("./ExplorerError.vue"));
const ExplorerLoader = defineAsyncComponent(
  () => import("./ExplorerLoader.vue")
);

// Importation des components Nuxt UI pour pouvoir les utiliser en JS
const contextRow = ref<TableRow<ApiFileItem> | null>(null);
const ui = { UCheckbox, UButton, UDropdownMenu, UIcon };
// Importation des colonnes et du système de sorting
const { columns } = useFileExplorerColumns(ui);
const sorting = ref([]);

// Variable "debounced" du loading
const loading_debounced = refDebounced(loading, 100);

function goBack() {
  const fs = useFSStore();

  if (fs.currentPath === "/" || fs.currentPath === "") return;

  const parts = fs.currentPath.split("/").filter(Boolean);
  parts.pop();

  const newPath = "/" + parts.join("/");
  fs.navigate(newPath || "/");
}

watch(
  () => fileTree,
  () => {
    rowSelection.value = {};
  },
  { deep: true }
);
</script>

<template>
  <ExplorerContextMenu :row="contextRow">
    <div class="h-full w-full overflow-y-hidden overflow-x-hidden">
      <UTable
        ref="table"
        v-model:sorting="sorting"
        v-model:row-selection="rowSelection"
        :loading="loading_debounced"
        loading-color="info"
        :data="fileTree"
        :columns="columns"
        :ui="{
          tbody: 'file-explorer-tbody',
          td: 'py-0',
        }"
        :virtualize="{
          estimateSize: 65,
          enabled: true,
          overscan: 5,
        }"
        @hover=""
        class="w-full h-full overflow-x-hidden"
        @contextmenu="(e, row) => (contextRow = row)"
      >
        <template #name-cell="{ row }">
          <FileExplorerTableRowFile :row="row" />
        </template>

        <!-- Page lorsque l'explorateur est vide  -->
        <template #empty>
          <div v-if="!hasError" class="flex items-center justify-center">
            <UEmpty
              class="min-w-125"
              variant="soft"
              icon="material-symbols:sad-tab-outline-rounded"
              title="No files"
              description="It looks like you haven't added any files/folders. Create one to get started."
              size="xl"
              :actions="[
                {
                  icon: 'material-symbols:keyboard-return-rounded',
                  label: 'Retour',
                  color: 'neutral',
                  variant: 'subtle',
                  size: 'md',
                  loadingAuto: true,
                  onClick: goBack,
                },
              ]"
            />
          </div>

          <ExplorerError
            v-if="hasError"
            :ErrorStatus="errorStatus"
            :message="errorMessage"
            :on-retry="retryFetching"
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
