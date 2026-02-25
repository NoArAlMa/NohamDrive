export type FileColumn = "last_modified" | "size";
export type FileViewMode = "list" | "tiles";

export function useFileExplorerSettings() {
  const { isMobile } = useResponsive();
  const visibleColumns = useState<FileColumn[]>("file-explorer-columns", () => [
    "last_modified",
  ]);
  const availableColumns = [
    { label: "Date", value: "last_modified" as FileColumn },
    { label: "Size", value: "size" as FileColumn },
  ];

  const viewMode = useState<FileViewMode>("file-explorer-view-mode", () => {
    if (import.meta.client) {
      const savedView = localStorage.getItem(
        "fileExplorerViewMode",
      ) as FileViewMode;
      return savedView === "list" || savedView === "tiles" ? savedView : "list";
    }
    return "list";
  });

  onMounted(() => {
    const savedColumns = localStorage.getItem("columns");
    if (savedColumns) {
      try {
        visibleColumns.value = JSON.parse(savedColumns);
      } catch {
        localStorage.removeItem("columns");
      }
    }

    if (import.meta.client) {
      const savedView = localStorage.getItem(
        "fileExplorerViewMode",
      ) as FileViewMode;
      if (savedView === "list" || savedView === "tiles") {
        viewMode.value = savedView;
      }
    }
  });

  watch(
    visibleColumns,
    (val) => {
      if (import.meta.client) {
        localStorage.setItem("columns", JSON.stringify(val));
      }
    },
    { deep: true },
  );

  watch(viewMode, (val) => {
    if (import.meta.client) {
      localStorage.setItem("fileExplorerViewMode", val);
    }
  });

  return {
    availableColumns,
    visibleColumns,
    viewMode,
  };
}
