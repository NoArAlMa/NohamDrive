<script lang="ts" setup>
const props = defineProps<{ selectedCount: number }>();
const { totalElements } = useFileTree();

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
  <!-- Sélection & nb éléments -->
  <!-- FINISH : Terminal -->
  <!-- TODO : Action en cours -->

  <div
    class="shrink-0 border-t min-h-6 px-3 py-0.5 w-full flex items-center justify-between"
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
