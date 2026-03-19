<script lang="ts" setup>
const fileTreeStore = useFileTree();
const { fileTree, loading, hasError, errorMessage, errorStatus } =
  storeToRefs(fileTreeStore);

const loading_debounced = refDebounced(loading, 100);

const selection = useFileExplorerSelection();

watch(fileTree, () => {
  selection.clear();
});

function updateSelection(item: ApiFileItem, checked: boolean) {
  selection.toggle(item, checked);
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
        :selected="selection.isSelected(item)"
        @update:selected="updateSelection"
      />
    </div>
  </LazyFileExplorerContextMenu>
</template>
