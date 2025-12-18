<script lang="ts" setup>
import type { TableColumn } from "@nuxt/ui";
import { h, resolveComponent } from "vue";
import type { Column } from "@tanstack/vue-table";
import { useVueTable } from "@tanstack/vue-table";
import type { ApiFileItem } from "~~/shared/types/file_tree";

const UCheckbox = resolveComponent("UCheckbox");
const UButton = resolveComponent("UButton");
const UDropdownMenu = resolveComponent("UDropdownMenu");
const UIcon = resolveComponent("UIcon");

const columns = ref<TableColumn<ApiFileItem>[]>([
  {
    id: "select",
    header: ({ table }) =>
      h(UCheckbox, {
        class: "rounded-full",
        modelValue: table.getIsSomePageRowsSelected()
          ? "indeterminate"
          : table.getIsAllPageRowsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          table.toggleAllPageRowsSelected(!!value),
        "aria-label": "Select all",
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        class: "rounded-full",
        modelValue: row.getIsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          row.toggleSelected(!!value),
        "aria-label": "Select row",
      }),
  },

  {
    accessorKey: "name",
    header: ({ column }) => getHeader(column, "Name"),
    cell: ({ row }) => {
      const isDir = row.original.is_dir;
      return h(
        "div",
        {
          class: isDir ? "flex items-center p-1 rounded" : "flex items-center",
        },
        [
          h(UIcon, {
            name: isDir ? "i-heroicons-folder" : "i-heroicons-document",
            class: "mr-2 text-lg",
          }),
          h("span", { class: "" }, row.getValue("name")),
        ]
      );
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

const data: ApiFileItem[] = [
  // Images
  {
    name: "vacances_2025.jpg",
    size: 3456789,
    is_dir: false,
    last_modified: "2025-12-18T10:30:00.000000Z",
  },
  {
    name: "logo_entreprise.png",
    size: 45678,
    is_dir: false,
    last_modified: "2025-12-17T15:45:00.000000Z",
  },
  {
    name: "capture_ecran.webp",
    size: 123456,
    is_dir: false,
    last_modified: "2025-12-16T09:10:00.000000Z",
  },

  // Documents
  {
    name: "CV_Maxime_Dupont.pdf",
    size: 256789,
    is_dir: false,
    last_modified: "2025-12-15T14:20:00.000000Z",
  },
  {
    name: "rapport_annuel_2025.docx",
    size: 1024567,
    is_dir: false,
    last_modified: "2025-12-14T11:30:00.000000Z",
  },
  {
    name: "presentation_projet.pptx",
    size: 5678901,
    is_dir: false,
    last_modified: "2025-12-13T16:50:00.000000Z",
  },

  // Archives
  {
    name: "backup_projet.zip",
    size: 10485760,
    is_dir: false,
    last_modified: "2025-12-12T12:15:00.000000Z",
  },
  {
    name: "anciens_documents.rar",
    size: 20971520,
    is_dir: false,
    last_modified: "2025-12-11T08:25:00.000000Z",
  },

  // Code
  {
    name: "script_automatisation.py",
    size: 12345,
    is_dir: false,
    last_modified: "2025-12-10T17:40:00.000000Z",
  },
  {
    name: "styles.css",
    size: 4567,
    is_dir: false,
    last_modified: "2025-12-09T10:55:00.000000Z",
  },

  // Dossiers
  {
    name: "Projets",
    size: 0,
    is_dir: true,
    last_modified: "2025-12-18T16:41:58.312000Z",
  },
  {
    name: "Images",
    size: 0,
    is_dir: true,
    last_modified: "2025-12-17T14:30:00.000000Z",
  },
  {
    name: "Documents_Importants",
    size: 0,
    is_dir: true,
    last_modified: "2025-12-16T12:00:00.000000Z",
  },

  // Fichiers spéciaux
  {
    name: ".env",
    size: 1234,
    is_dir: false,
    last_modified: "2025-12-05T09:10:00.000000Z",
  },
  {
    name: "README.md",
    size: 5678,
    is_dir: false,
    last_modified: "2025-12-04T15:20:00.000000Z",
  },
  {
    name: "fichier_sans_extension",
    size: 7890,
    is_dir: false,
    last_modified: "2025-12-03T11:35:00.000000Z",
  },
];

const sorting = ref([
  {
    id: "name",
    desc: false,
  },
]);

function getHeader(column: Column<ApiFileItem>, label: string) {
  const isSorted = column.getIsSorted();

  return h(
    UDropdownMenu,
    {
      content: {
        align: "start",
      },
      "aria-label": "Actions dropdown",
      items: [
        {
          label: "Asc",
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
          label: "Desc",
          icon: "i-lucide-arrow-down-wide-narrow",
          type: "checkbox",
          checked: isSorted === "desc",
          onSelect: () => {
            if (isSorted === "desc") {
              column.clearSorting();
            } else {
              column.toggleSorting(true);
            }
          },
        },
      ],
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

const items_breadcrumb = ref([
  {
    label: "Mes fichiers",
  },
  {
    label: "Bonjour",
  },
  {
    label: "Rebonjour",
    onClick: () => console.log("Salut"),
  },
]);
</script>

<template>
  <div class="flex flex-col">
    <section class="flex items-center">
      <UBreadcrumb :items="items_breadcrumb"> </UBreadcrumb>
    </section>
    <section>
      <UTable v-model:sorting="sorting" :data="data" :columns="columns" @hover="">
        <template #name-cell> </template>
      </UTable>
    </section>
  </div>
</template>
