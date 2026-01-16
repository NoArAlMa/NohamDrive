<script lang="ts" setup>
const props = defineProps<{
  items: ApiFileItem[];
}>();

const action = useFsActions();

function forEachSelected(action: (item: ApiFileItem) => void | Promise<void>) {
  for (const item of props.items) {
    action(item);
  }
}
</script>

<template>
  <Transition name="slide-fade" appear>
    <section class="px-4 py-2 flex gap-2 w-full h-full shadow-sm rounded-xl">
      <UButton
        leading-icon="material-symbols:share-windows-rounded"
        label="Partager"
        color="neutral"
        variant="ghost"
        class="px-2 py-1"
        disabled
        @click=""
      />

      <UButton
        leading-icon="material-symbols:download-rounded"
        label="Télécharger"
        color="neutral"
        variant="ghost"
        class="px-2 py-1"
        @click="forEachSelected(action.download)"
      />
      <UButton
        leading-icon="material-symbols:drive-file-move-outline-rounded"
        label="Déplacer"
        color="neutral"
        variant="ghost"
        disabled
        class="px-2 py-1"
      />
      <UButton
        leading-icon="material-symbols:delete-outline-rounded"
        label="Supprimer"
        color="error"
        variant="ghost"
        class="ml-2 px-2 py-1"
        @click="forEachSelected(action.del)"
      />
    </section>
  </Transition>
</template>

<style scoped>
.slide-fade-enter-from,
.slide-fade-appear-from {
  opacity: 0;
  transform: translateY(12px);
}

.slide-fade-enter-to,
.slide-fade-appear-to {
  opacity: 1;
  transform: translateY(0);
}

.slide-fade-enter-active,
.slide-fade-appear-active {
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}
</style>
