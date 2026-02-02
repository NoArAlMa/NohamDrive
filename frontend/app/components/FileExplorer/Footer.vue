<script lang="ts" setup>
const props = defineProps<{ selectedCount: number }>();
const filetree = useFileTree();
const { totalElements } = storeToRefs(filetree);

const selectionLabel = computed(() => {
  if (props.selectedCount === 0) {
    return `${totalElements.value} éléments`;
  }

  return `${props.selectedCount} sélectionné${
    props.selectedCount > 1 ? "s" : ""
  }`;
});
</script>

<template>
  <!-- MAYBE : Basculement de vue -->
  <!-- FINISH : Terminal -->

  <div
    class="shrink-0 border-t min-h-6 pl-3 px-2 py-0.5 w-full flex items-center justify-between"
  >
    <div>
      <span>{{ selectionLabel }}</span>
    </div>

    <UButton
      v-if="totalElements > 0"
      leading-icon="material-symbols:terminal-rounded"
      variant="ghost"
      label="Ouvrir dans terminal"
      color="neutral"
      class="py-0.5"
    />
  </div>
</template>
