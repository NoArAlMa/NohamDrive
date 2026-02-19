<script lang="ts" setup>
const props = defineProps<{ selectedCount: number }>();
const filetree = useFileTree();
const { totalElements } = storeToRefs(filetree);
const { isMobile } = useResponsive();

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
  <div
    class="shrink-0 border-t border-neutral-300 min-h-6 pl-3 pt-1 w-full flex items-center justify-between"
  >
    <div>
      <span>{{ selectionLabel }}</span>
    </div>

    <UButton
      v-if="totalElements > 0 && !isMobile"
      leading-icon="mdi:star-four-points-outline"
      variant="ghost"
      label="Ouvrir avec Echo"
      color="neutral"
      class="py-1"
      @click="navigateTo('/terminal')"
    />
  </div>
</template>
