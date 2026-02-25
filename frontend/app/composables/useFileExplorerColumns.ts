import { h } from "vue";
import type { TableColumn, TableRow } from "@nuxt/ui";
import type { Column } from "@tanstack/vue-table";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import formatDate from "~/utils/date";

type UIComponents = {
  UCheckbox: any;
  UButton: any;
  UDropdownMenu: any;
  UIcon: any;
};

export function useFileExplorerColumns(
  ui: UIComponents,
  isMobile: Ref<boolean>,
) {
  const { visibleColumns } = useFileExplorerSettings();

  function sortingItems(column: Column<ApiFileItem>) {
    const isSorted = column.getIsSorted();

    return [
      {
        label: "Ascendant",

        icon: "material-symbols:arrow-upward-rounded",
        type: "checkbox",
        checked: isSorted === "asc",
        onSelect: () =>
          isSorted === "asc"
            ? column.clearSorting()
            : column.toggleSorting(false),
      },
      {
        label: "Descendant",

        icon: "material-symbols:arrow-downward-rounded",
        type: "checkbox",
        checked: isSorted === "desc",
        onSelect: () =>
          isSorted === "desc"
            ? column.clearSorting()
            : column.toggleSorting(true),
      },
    ];
  }

  function getHeader(column: Column<ApiFileItem>, label: string) {
    const isSorted = column.getIsSorted();

    return h(ui.UDropdownMenu, { items: sortingItems(column) }, () =>
      h(ui.UButton, {
        label,
        variant: "ghost",
        color: "neutral",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up"
            : "i-lucide-arrow-down"
          : "i-lucide-arrow-up-down",
      }),
    );
  }

  const columns = computed<TableColumn<ApiFileItem>[]>(() => {
    const baseColumns: TableColumn<ApiFileItem>[] = [];

    if (!isMobile.value) {
      baseColumns.push({
        id: "select",
        minSize: 30,
        maxSize: 60,
        size: 40,
        header: ({ table }) =>
          h(ui.UCheckbox, {
            ui: { base: "rounded-full" },

            modelValue: table.getIsAllPageRowsSelected(),
            indeterminate: table.getIsSomePageRowsSelected(),
            "onUpdate:modelValue": (value: boolean) =>
              table.toggleAllPageRowsSelected(value),
            icon: "material-symbols:check-rounded",
          }),
        cell: ({ row }) =>
          h(ui.UCheckbox, {
            ui: { base: "rounded-full" },
            modelValue: row.getIsSelected(),
            "onUpdate:modelValue": (value: boolean) =>
              row.toggleSelected(value),
            icon: "material-symbols:check-rounded",
          }),
      });
    }

    baseColumns.push({
      accessorKey: "name",
      size: 300,
      minSize: 200,
      maxSize: 500,
      header: ({ column }) =>
        h("div", { class: "flex items-center gap-2" }, [
          h(ui.UIcon, { name: "i-heroicons-document", class: "text-lg" }),
          getHeader(column, "Name"),
        ]),
    });

    if (!isMobile.value && visibleColumns.value.includes("last_modified")) {
      baseColumns.push({
        accessorKey: "last_modified",
        minSize: 100,
        maxSize: 250,
        size: 150,
        header: ({ column }) => getHeader(column, "Date"),
        cell: ({ row }) => formatDate(row.getValue("last_modified")),
      });
    }

    if (!isMobile.value && visibleColumns.value.includes("size")) {
      baseColumns.push({
        accessorKey: "size",
        minSize: 100,
        maxSize: 250,
        size: 150,
        header: ({ column }) => getHeader(column, "Size"),
        cell: ({ row }) => formatFileSize(row.getValue("size") || 0),
      });
    }
    return baseColumns;
  });

  return { columns };
}
