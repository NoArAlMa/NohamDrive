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
    class="shrink-0 min-h-6 pl-1 pt-1 w-full flex items-center justify-between"
  >
    <div class="rounded-md px-2.5 py-1 md:border border-muted shadow-sm">
      <span>{{ selectionLabel }}</span>
    </div>

    <UButton
      v-if="!isMobile"
      leading-icon="terminal:echo-icon"
      variant="outline"
      label="Ouvrir avec Echo"
      color="neutral"
      :ui="{
        base: 'px-2 py-1.5',
        leadingIcon: 'text-primary',
      }"
      @click="navigateTo('/terminal')"
    />
  </div>
</template>
