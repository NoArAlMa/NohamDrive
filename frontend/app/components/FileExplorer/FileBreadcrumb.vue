<script lang="ts" setup>
import type { BreadcrumbItem } from "@nuxt/ui";

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
  <UBreadcrumb :items="items">
    <template #item="{ item }">
      <ULink
        size="lg"
        class="px-0 hover:cursor-pointer"
        @click="handleClick(item.path)"
      >
        {{ item.label }}
      </ULink>
    </template>
  </UBreadcrumb>
</template>
