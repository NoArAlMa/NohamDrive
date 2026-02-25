<script lang="ts" setup>
import { useFSStore } from "#imports";

const fileTreeStore = useFileTree();
const fsstore = useFSStore();
const { fileTree, loading, hasError, errorMessage, errorStatus } =
  storeToRefs(fileTreeStore);

const emit = defineEmits<{
  (e: "update:selectedItems", value: ApiFileItem[]): void;
  (e: "update:selectedCount", value: number): void;
}>();

function goBack() {
  const fs = useFSStore();
  fs.navigate("..");
}

const loading_debounced = refDebounced(loading, 100);

const localSelection = ref<ApiFileItem[]>([]);

function clearSelection() {
  localSelection.value = [];
  emit("update:selectedItems", []);
  emit("update:selectedCount", 0);
}

defineExpose({
  clearSelection,
});

const validSelection = computed(() => {
  const validNames = new Set(fileTree.value.map((i) => i.name));

  return localSelection.value.filter((selected) =>
    validNames.has(selected.name),
  );
});

watch(
  () => fsstore.currentPath,
  () => {
    localSelection.value = [];
    emit("update:selectedItems", []);
    emit("update:selectedCount", 0);
  },
);

function updateSelection(item: ApiFileItem, checked: boolean) {
  if (checked) {
    if (!localSelection.value.includes(item)) {
      localSelection.value.push(item);
    }
  } else {
    localSelection.value = localSelection.value.filter((i) => i !== item);
  }

  emit("update:selectedItems", localSelection.value);
  emit("update:selectedCount", localSelection.value.length);
}
</script>

<template>
  <LazyFileExplorerContextMenu :row="null">
    <div
      class="flex items-center justify-center h-full"
      v-if="loading_debounced"
    >
      <UIcon
        name="material-symbols:progress-activity"
        class="animate-spin size-30"
      />
    </div>

    <div class="flex items-center justify-center h-full" v-else-if="hasError">
      <FileExplorerError
        :ErrorStatus="errorStatus"
        :message="errorMessage"
        :on-retry="useFileTree().retryFetching"
      />
    </div>

    <div
      class="flex items-center justify-center h-full"
      v-else-if="fileTree.length === 0"
    >
      <LazyUEmpty
        class="min-w-125"
        variant="soft"
        icon="material-symbols:sad-tab-outline-rounded"
        title="No files"
        description="It looks like you haven't added any files/folders. Create one to get started."
        size="xl"
        :actions="[
          {
            icon: 'material-symbols:keyboard-return-rounded',
            label: 'Retour',
            color: 'neutral',
            variant: 'subtle',
            size: 'md',
            loadingAuto: true,
            onClick: goBack,
          },
        ]"
      />
    </div>

    <div
      class="grid grid-cols-[repeat(auto-fill,minmax(140px,1fr))] auto-rows-min content-start gap-4 p-4 h-full overflow-y-auto"
      v-else
    >
      <FileExplorerTiles
        v-for="item in fileTree"
        :key="item.name"
        :item="item"
        :selected="validSelection.includes(item)"
        @update:selected="updateSelection"
      />
    </div>
  </LazyFileExplorerContextMenu>
</template>
