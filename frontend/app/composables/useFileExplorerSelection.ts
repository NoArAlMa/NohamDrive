import type { ApiFileItem } from "~~/shared/types/file_tree";

export function useFileExplorerSelection() {
  const selected = useState<Set<ApiFileItem>>(
    "file-explorer-selection",
    () => new Set(),
  );

  const items = computed(() => Array.from(selected.value));
  const count = computed(() => selected.value.size);

  function add(item: ApiFileItem) {
    selected.value.add(item);
  }

  function remove(item: ApiFileItem) {
    selected.value.delete(item);
  }

  function toggle(item: ApiFileItem, checked?: boolean) {
    if (checked === true) {
      selected.value.add(item);
      return;
    }

    if (checked === false) {
      selected.value.delete(item);
      return;
    }

    if (selected.value.has(item)) {
      selected.value.delete(item);
    } else {
      selected.value.add(item);
    }
  }

  function clear() {
    selected.value.clear();
  }

  function set(items: ApiFileItem[]) {
    selected.value = new Set(items);
  }

  function isSelected(item: ApiFileItem) {
    return selected.value.has(item);
  }

  return {
    selected,
    items,
    count,
    add,
    remove,
    toggle,
    clear,
    set,
    isSelected,
  };
}
