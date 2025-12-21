// composables/useFsActions.ts
import type { ApiFileItem } from "~~/shared/types/file_tree";

export const useFsActions = () => {
  const FSStore = useFSStore();
  const open = (item: ApiFileItem) => {
    if (item.is_dir) {
      FSStore.navigate(item.name);
    }
  };
  const rename = (item: ApiFileItem) => {
    /* ... */
  };
  const del = (item: ApiFileItem) => {
    /* ... */
  };
  const property = (item: ApiFileItem) => {
    /* ... */
  };
  const terminal = (item: ApiFileItem) => {
    /* ... */
  };
  const download = (item: ApiFileItem) => {
    /* ... */
  };

  return { open, rename, del, property, terminal, download };
};
