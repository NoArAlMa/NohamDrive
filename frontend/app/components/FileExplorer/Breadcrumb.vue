<script lang="ts" setup>
const { setCurrentPath, generateBreadcrumbItems } = useFSStore();

const items = computed(() => {
  return generateBreadcrumbItems();
});

// Fonction pour gérer le clic
function handleClick(path: string) {
  setCurrentPath(path);
}
</script>

<template>
  <div class="bg-gray/50">
    <UBreadcrumb
      :ui="{
        list: 'flex items-center gap-0',
        link: 'group flex items-center gap-0',
        separatorIcon: '-mx-0.5',
      }"
      :items="items"
      separator-icon="mdi:slash-forward"
    >
      <template #item="{ item }">
        <ULink
          size="lg"
          class="mx-0 px-1.5 py-1 rounded-md hover:cursor-pointer hover:bg-gray-600/25"
          @click="handleClick(item.path)"
        >
          {{ item.label }}
        </ULink>
      </template>
    </UBreadcrumb>
  </div>
</template>
