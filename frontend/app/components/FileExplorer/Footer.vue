<script lang="ts" setup>
const props = defineProps<{ selectedCount: number }>();
const { totalElements } = useFileTree();
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
      <span v-if="!props.selectedCount"> {{ totalElements }} éléments </span>
      <span v-else>
        {{ props.selectedCount }} sélectionné<span
          v-if="props.selectedCount > 1"
          >s</span
        >
      </span>
    </div>

    <UButton
      leading-icon="material-symbols:terminal-rounded"
      variant="ghost"
      label="Ouvrir dans terminal"
      color="neutral"
      class="py-0.5"
    />
  </div>
</template>
