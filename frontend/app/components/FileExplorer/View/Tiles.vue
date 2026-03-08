<script lang="ts" setup>
const fileTreeStore = useFileTree();
const { fileTree, loading, hasError, errorMessage, errorStatus } =
  storeToRefs(fileTreeStore);

onMounted(() => {
  emit("update:selectedCount", 0);
  emit("update:selectedItems", []);
});

const emit = defineEmits<{
  (e: "update:selectedItems", value: ApiFileItem[]): void;
  (e: "update:selectedCount", value: number): void;
}>();

const emitSelection = useDebounceFn(() => {
  emit("update:selectedItems", Array.from(localSelection.value));
  emit("update:selectedCount", localSelection.value.size);
}, 100);

const loading_debounced = refDebounced(loading, 100);

const localSelection = ref<Set<ApiFileItem>>(new Set());

function clearSelection() {
  localSelection.value.clear();
  emitSelection();
}

defineExpose({
  clearSelection,
});

watch(fileTree, () => {
  clearSelection();
});

function updateSelection(item: ApiFileItem, checked: boolean) {
  if (checked) {
    localSelection.value.add(item);
  } else {
    localSelection.value.delete(item);
  }
  emitSelection();
}
</script>

<template>
  <LazyFileExplorerContextMenu :row="null">
    <div
      class="flex items-center justify-center h-full"
      v-if="loading_debounced"
    >
      <LazyFileExplorerLoaderTile />
    </div>

    <div class="flex items-center justify-center h-full" v-else-if="hasError">
      <LazyFileExplorerError
        :ErrorStatus="errorStatus"
        :message="errorMessage"
        :on-retry="useFileTree().retryFetching"
      />
    </div>

    <div
      class="flex items-center justify-center h-full"
      v-else-if="fileTree.length === 0"
    >
      <FileExplorerEmpty />
    </div>

    <div
      class="grid grid-cols-[repeat(auto-fill,minmax(140px,1fr))] auto-rows-min content-start justify-items-center gap-4 p-4 h-full overflow-y-auto rounded-md"
      v-else
    >
      <LazyFileExplorerElementsTile
        v-for="item in fileTree"
        :key="item.name"
        :item="item"
        :selected="localSelection.has(item)"
        @update:selected="updateSelection"
      />
    </div>
  </LazyFileExplorerContextMenu>
</template>
