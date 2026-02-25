export type FileColumn = "last_modified" | "size" | "type";

export function useFileExplorerSettings() {
  const visibleColumns = useState<FileColumn[]>("file-explorer-columns", () => [
    "last_modified",
  ]);

  const availableColumns = [
    { label: "Date", value: "last_modified" as FileColumn },
    { label: "Size", value: "size" as FileColumn },
    { label: "Type", value: "type" as FileColumn },
  ];

  onMounted(() => {
    const saved = localStorage.getItem("columns");
    if (saved) {
      try {
        visibleColumns.value = JSON.parse(saved);
      } catch {
        localStorage.removeItem("columns");
      }
    }
  });

  watch(
    visibleColumns,
    (val) => {
      localStorage.setItem("columns", JSON.stringify(val));
    },
    { deep: true },
  );

  return {
    availableColumns,
    visibleColumns,
  };
}
