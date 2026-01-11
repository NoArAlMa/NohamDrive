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
    <UBreadcrumb :items="items" separator-icon="mdi:slash-forward">
      <template #item="{ item }">
        <ULink
          size="lg"
          class="p-1 rounded-md hover:cursor-pointer hover:bg-gray-600/50"
          @click="handleClick(item.path)"
        >
          {{ item.label }}
        </ULink>
      </template>
    </UBreadcrumb>
  </div>
</template>
