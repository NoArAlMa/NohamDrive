import { h } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { Column } from "@tanstack/vue-table";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import formatDate from "~/utils/date";

type UIComponents = {
  Checkbox: any;
  Button: any;
  DropdownMenu: any;
  Icon: any;
};

export function useFileExplorerColumns(ui: UIComponents) {
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

    return h(ui.DropdownMenu, { items: sortingItems(column) }, () =>
      h(ui.Button, {
        label,
        variant: "ghost",
        color: "neutral",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up"
            : "i-lucide-arrow-down"
          : "i-lucide-arrow-up-down",
      })
    );
  }

  const columns = shallowRef<TableColumn<ApiFileItem>[]>([
    {
      id: "select",
      header: ({ table }) =>
        h(ui.Checkbox, {
          ui: { base: "rounded-full" },
          modelValue: table.getIsAllPageRowsSelected(),
          indeterminate: table.getIsSomePageRowsSelected(),
          "onUpdate:modelValue": (value: boolean) =>
            table.toggleAllPageRowsSelected(value),
        }),
      cell: ({ row }) =>
        h(ui.Checkbox, {
          ui: { base: "rounded-full" },
          modelValue: row.getIsSelected(),
          "onUpdate:modelValue": (value: boolean) => row.toggleSelected(value),
        }),
    },
    {
      accessorKey: "name",
      header: ({ column }) =>
        h("div", { class: "flex items-center gap-2" }, [
          h(ui.Icon, { name: "i-heroicons-document", class: "text-lg" }),
          getHeader(column, "Name"),
        ]),
    },
    {
      accessorKey: "last_modified",
      header: ({ column }) => getHeader(column, "Date"),
      cell: ({ row }) => formatDate(row.getValue("last_modified")),
    },
  ]);

  return { columns };
}
