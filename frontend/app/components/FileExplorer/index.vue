<script lang="ts" setup>
import type { TableRow } from "@nuxt/ui";
import { resolveComponent } from "vue";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import ExplorerContextMenu from "./ExplorerContextMenu.vue";
import ExplorerError from "./ExplorerError.vue";
import ExplorerLoader from "./ExplorerLoader.vue";

const {
  fileTree,
  hasError,
  errorMessage,
  errorStatus,
  loading,
  retryFetching,
} = useFileTree();

const table = useTemplateRef("table");

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

const rowSelection = ref<Record<string, boolean>>({});

const selectedCount = computed(
  () => Object.values(rowSelection.value).filter(Boolean).length
);

const selectedRows = computed(() =>
  fileTree.value.filter((_, index) => rowSelection.value[index])
);
const emit = defineEmits<{
  (e: "update:selectedCount", count: number): void;
}>();

watch(selectedCount, (count) => emit("update:selectedCount", count), {
  immediate: true,
});

const { drawerOpen, currentItemProperties, closeDrawer } = usePropertyDrawer();
</script>

<template>
  <ExplorerContextMenu :row="contextRow">
    <div class="h-full w-full overflow-y-hidden overflow-x-hidden">
      <UTable
        ref="table"
        v-model:sorting="sorting"
        v-model:row-selection="rowSelection"
        :loading="loading"
        loading-color="info"
        :data="fileTree"
        :columns="columns"
        :ui="{
          tbody: 'file-explorer-tbody',
        }"
        :virtualize="{
          estimateSize: 65,
          enabled: true,
          overscan: 8,
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

  <USlideover v-model:open="drawerOpen" side="right">
    <template #content>
      <div class="p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Propriétés</h3>
          <UButton
            color="neutral"
            variant="ghost"
            icon="i-heroicons-x-mark-20-solid"
            @click="closeDrawer"
          />
        </div>
        <div v-if="currentItemProperties" class="space-y-4">
          <p><strong>Nom:</strong> {{ currentItemProperties.nom }}</p>
          <p>
            <strong>Type:</strong>
            {{ currentItemProperties.taille_ko == 0 ? "Dossier" : "Fichier" }}
          </p>
          <p>
            <strong>Taille:</strong>
            {{ currentItemProperties.taille_octets }} octets
          </p>
          <p>
            <strong>Dernière modification:</strong>
            {{
              new Date(currentItemProperties.date_modification).toLocaleString()
            }}
          </p>
        </div>
      </div>
    </template>
  </USlideover>
</template>
