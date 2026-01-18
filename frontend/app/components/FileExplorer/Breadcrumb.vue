<script lang="ts" setup>
defineNuxtComponent({
  ssr: false,
});

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
  <ClientOnly>
    <Transition name="slide-fade" appear>
      <div class="bg-gray/50">
        <UBreadcrumb
          :ui="{
            list: 'flex items-center gap-0.5',
            link: 'group flex items-center gap-1',
          }"
          :items="items"
        >
          <template #separator>
            <span class="text-muted">/</span>
          </template>
          <template #item="{ item }">
            <ULink
              class="mx-0 px-2 py-1 rounded-md hover:cursor-pointer hover:bg-gray-600/25"
              @click="handleClick(item.path)"
            >
              {{ item.label }}
            </ULink>
          </template>
        </UBreadcrumb>
      </div>
    </Transition>
  </ClientOnly>
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
  transition:
    opacity 200ms ease-out,
    transform 200ms ease-out;
}
</style>
