<script lang="ts" setup>
import type { ContextMenuItem, TableColumn, TableRow } from "@nuxt/ui";
import { h, resolveComponent } from "vue";
import type { Column } from "@tanstack/vue-table";
import type { ApiFileItem } from "~~/shared/types/file_tree";

const FSStore = useFSStore();

const {
  fileTree,
  hasError,
  errorMessage,
  errorStatus,
  enterFolder,
  loading,
  retryFetching,
} = useFileTree();

// Importation des components Nuxt UI pour pouvoir les utiliser en JS

const UCheckbox = resolveComponent("UCheckbox");
const UButton = resolveComponent("UButton");
const UDropdownMenu = resolveComponent("UDropdownMenu");
const UIcon = resolveComponent("UIcon");

// Variable "debounced" du loading

const loading_debounced = refDebounced(loading, 100);

// Variable qui regroupe les actions disponible dans le context-menu

const fsActions = {
  open: (item: ApiFileItem) => {},
  rename: (item: ApiFileItem) => {},
  delete: (item: ApiFileItem) => {},
  property: (item: ApiFileItem) => {},
  terminal: (item: ApiFileItem) => {},
  download: (item: ApiFileItem) => {},
};

//// Toutes les fonctions sur les colonnes, tris et headers

// Variable qui définis et stock les colonnes de l'explorateur

const columns = ref<TableColumn<ApiFileItem>[]>([
  {
    id: "select",
    header: ({ table }) =>
      h(UCheckbox, {
        ui: {
          base: "rounded-full",
        },
        modelValue: table.getIsSomePageRowsSelected()
          ? "indeterminate"
          : table.getIsAllPageRowsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          table.toggleAllPageRowsSelected(!!value),
        "aria-label": "Select all",
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        ui: {
          base: "rounded-full",
        },
        modelValue: row.getIsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          row.toggleSelected(!!value),
        "aria-label": "Select row",
      }),
  },

  {
    accessorKey: "name",
    header: ({ column }) => {
      return h("div", { class: "flex items-center" }, [
        h(UIcon, {
          name: "i-heroicons-document",
          class: "mr-4 text-lg",
        }),
        getHeader(column, "Name"),
      ]);
    },
  },
  {
    accessorKey: "last_modified",
    header: ({ column }) => getHeader(column, "Date"),
    cell: ({ row }) => {
      try {
        return new Date(row.getValue("last_modified")).toLocaleString("fr-FR", {
          day: "numeric",
          month: "short",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
      } catch {
        return row.getValue("last_modified");
      }
    },
  },
]);

// Variable d'initiation du tri

const sorting = ref([
  {
    id: "name",
    desc: false,
  },
]);

// Fonction qui garde et permet de gérer le html des dropdown qui tris

function sortingItems(column: Column<ApiFileItem>) {
  const isSorted = column.getIsSorted();

  return [
    {
      label: "Ascendant",
      type: "checkbox",
      icon: "i-lucide-arrow-up-narrow-wide",
      checked: isSorted === "asc",
      onSelect: () => {
        if (isSorted === "asc") {
          column.clearSorting();
        } else {
          column.toggleSorting(false);
        }
      },
    },
    {
      label: "Descendant",
      type: "checkbox",
      icon: "i-lucide-arrow-down-wide-narrow",
      checked: isSorted === "desc",
      onSelect: () => {
        if (isSorted === "desc") {
          column.clearSorting();
        } else {
          column.toggleSorting(true);
        }
      },
    },
  ];
}

// Fonction pour créer les dropdown qui permettent de trier une colonne

function getHeader(column: Column<ApiFileItem>, label: string) {
  const isSorted = column.getIsSorted();

  return h(
    UDropdownMenu,
    {
      content: {
        align: "start",
      },
      "aria-label": "Actions dropdown",
      items: [...sortingItems(column)],
    },
    () =>
      h(UButton, {
        color: "neutral",
        variant: "ghost",
        label,
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5 data-[state=open]:bg-elevated",
        "aria-label": `Sort by ${
          isSorted === "asc" ? "descending" : "ascending"
        }`,
      })
  );
}

// Les items qui compose le ContextMenu
const items = ref<ContextMenuItem[]>([]);

// Fonction pour créer les éléments du context-menu avec les informations de la ligne

function getRowItems(row: TableRow<ApiFileItem>): ContextMenuItem[] {
  if (row.original.is_dir) {
    return [
      {
        label: "Ouvrir dans le terminal",
        icon: "material-symbols:terminal-rounded",
        onSelect() {
          fsActions.terminal(row.original);
        },
      },
      {
        type: "separator" as const,
      },
      {
        label: "Ouvrir le dossier",
        icon: "material-symbols:folder-open-outline-rounded",
        onSelect() {
          handleRowClick(row);
        },
      },
      {
        label: "Renommer",
        icon: "material-symbols:edit-outline-rounded",
        onSelect() {
          fsActions.rename(row.original);
        },
      },
      {
        label: "Supprimer",
        icon: "material-symbols:delete-outline-rounded",
        color: "error" as const,
        onSelect() {
          fsActions.delete(row.original);
        },
      },
      {
        type: "separator" as const,
      },
      {
        label: "Propriétés",
        icon: "material-symbols:info-outline-rounded",
        onSelect() {
          fsActions.property(row.original);
        },
      },
    ];
  } else {
    return [
      {
        label: "Visualiser",
        icon: "material-symbols:visibility-outline-rounded",
        onSelect() {
          console.log("Visualiser :", row.original);
        },
      },

      {
        type: "separator" as const,
      },
      {
        label: "Télécharger",
        icon: "material-symbols:download-rounded",
        onSelect() {
          fsActions.download(row.original);
        },
      },
      {
        label: "Renommer",
        icon: "material-symbols:edit-outline-rounded",
        onSelect() {
          fsActions.rename(row.original);
        },
      },
      {
        label: "Supprimer",
        icon: "material-symbols:delete-outline-rounded",
        color: "error" as const,
        onSelect() {
          fsActions.delete(row.original);
        },
      },
      {
        type: "separator" as const,
      },
      {
        type: "label",
        label: "Propriétés",
        icon: "material-symbols:info-outline-rounded",
        onSelect() {
          fsActions.property(row.original);
        },
      },
    ];
  }
}

// Fonction à l'ouverture du context-menu (clique droit)

function onContextmenu(_e: Event, row: TableRow<ApiFileItem>) {
  items.value = getRowItems(row);
}

// Fonction qui gère le clique sur une ligne

const handleRowClick = async (row: TableRow<ApiFileItem>) => {
  if (!row.original.is_dir) return;

  enterFolder(row.original.name);
};

// Fonction qui gère le clique sur le Breadcrumb

const onBreadcrumbClick = async (path: string) => {
  FSStore.setCurrentPath(path);
};
</script>

<template>
  <div class="flex flex-col">
    <section class="flex items-center justify-between mb-2">
      <UBreadcrumb :items="FSStore.generateBreadcrumbItems()">
        <template #item="{ item }">
          <UButton
            variant=""
            size="lg"
            class="px-0 hover:cursor-pointer"
            @click="onBreadcrumbClick(item.path)"
          >
            {{ item.label }}
          </UButton>
        </template>
      </UBreadcrumb>
    </section>
    <section>
      <UContextMenu :items="items">
        <UTable
          v-model:sorting="sorting"
          :loading="loading_debounced"
          :sticky="true"
          :data="fileTree"
          :columns="columns"
          :ui="{
            tbody: 'file-explorer-tbody',
          }"
          class="max-h-[600px] overflow-y-scroll"
          @hover=""
          @contextmenu="onContextmenu"
        >
          <!-- Template pour modifier la ligne et ajouter le clique et les images pour les fichiers -->

          <template #name-cell="{ row }">
            <div
              class="relative h-full flex items-center group"
              @click="row.toggleSelected()"
              @dblclick="handleRowClick(row)"
            >
              <UIcon
                v-if="row.original.is_dir"
                name="heroicons:folder"
                class="text-lg mr-2"
              />

              <UIcon
                v-else
                :name="getFileIcon(row.original.name)"
                class="text-lg mr-2"
                :alt="`Icon for ${row.original.name}`"
              />

              <ULink>
                <span
                  class="hover:underline underline-offset-2 cursor-pointer"
                  @click="handleRowClick(row)"
                >
                  {{ row.getValue("name") }}
                </span>
              </ULink>
            </div>
          </template>

          <!-- Page lorsque l'explorateur est vide  -->

          <template #empty>
            <!-- Si il n'y a pas de fichiers -->

            <div
              v-if="!loading && !hasError"
              class="flex items-center justify-center"
            >
              <UEmpty
                class="min-w-[500px]"
                variant="soft"
                icon="material-symbols:sad-tab-outline-rounded"
                title="No files"
                description="It looks like you haven't added any files/folders.
              Create one to get started."
                size="xl"
              />
            </div>

            <!-- Si on a une erreur au niveau du serveur -->

            <div v-if="hasError" class="flex items-center justify-center">
              <UEmpty
                class="min-w-[500px]"
                variant="soft"
                icon="material-symbols:error-outline-rounded"
                :description="errorMessage"
                :actions="
                  errorStatus === 500
                    ? [
                        {
                          icon: 'material-symbols:sync-rounded',
                          label: 'Refresh',
                          color: 'neutral',
                          variant: 'subtle',
                          size: 'md',
                          loadingAuto: true,
                          onClick: retryFetching,
                        },
                      ]
                    : []
                "
                size="xl"
              >
                <template #title>
                  <div>
                    <h1
                      :class="
                        errorStatus === 500 ? 'text-error' : 'text-warning'
                      "
                    >
                      Erreur {{ errorStatus }}
                    </h1>
                  </div>
                </template>
              </UEmpty>
            </div>
          </template>

          <!-- Page pour le chargement de l'explorateur -->

          <template #loading>
            <div class="space-y-2 px-4 py-3">
              <div v-for="i in 6" :key="i" class="flex items-center gap-1">
                <USkeleton class="h-[50px] w-full rounded-none" />
              </div>
            </div>
          </template>
        </UTable>
      </UContextMenu>
    </section>
  </div>
</template>
