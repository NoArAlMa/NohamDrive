<script lang="ts" setup>
defineNuxtComponent({
  ssr: false,
});

const { setCurrentPath, generateBreadcrumbItems, navigate } = useFSStore();

const { isRoot } = storeToRefs(useFSStore());
const { isMobile } = useResponsive();

const items = computed(() => {
  return generateBreadcrumbItems();
});

// Fonction pour gérer le clic
function handleClick(path: string) {
  setCurrentPath(path);
}

function handleReturn() {
  navigate("..");
}
</script>

<template>
  <ClientOnly>
    <Transition name="slide-fade" appear>
      <div v-if="!isMobile">
        <UBreadcrumb
          :items="items"
          overflow="ellipsis"
          :max-items="4"
          :ui="{
            root: '',
            list: 'flex items-center gap-0.5 min-w-0',
            item: 'min-w-0',
            link: 'group flex items-center gap-1 truncate',
          }"
        >
          <template #separator>
            <span class="text-muted shrink-0">/</span>
          </template>

          <template #item="{ item }">
            <ULink
              class="mx-0 px-2 py-1 rounded-md hover:bg-elevated truncate max-w-40"
              :title="item.label"
              @click="handleClick(item.path)"
            >
              {{ item.label }}
            </ULink>
          </template>
        </UBreadcrumb>
      </div>
      <div v-else-if="isMobile && !isRoot">
        <UButton
          icon="material-symbols:keyboard-backspace-rounded"
          variant="ghost"
          color="neutral"
          @click="handleReturn"
        />
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
