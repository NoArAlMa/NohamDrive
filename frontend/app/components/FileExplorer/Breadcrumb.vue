<script lang="ts" setup>
const action = useFsActions();

const { setCurrentPath, generateBreadcrumbItems, navigate } = useFSStore();

const { isRoot } = storeToRefs(useFSStore());
const { isMobile } = useResponsive();

const items = computed(() => {
  return generateBreadcrumbItems();
});

function handleClick(path: string) {
  setCurrentPath(path);
}

function handleReturn() {
  navigate("..");
}

const dragOverPath = ref<string | null>(null);

function onDragOverCrumb(e: DragEvent, path: string) {
  e.preventDefault();
  e.dataTransfer!.dropEffect = "move";
  dragOverPath.value = path;
}

function onDragLeaveCrumb() {
  dragOverPath.value = null;
}

async function onDropCrumb(e: DragEvent, path: string) {
  e.preventDefault();

  let data;
  try {
    data = JSON.parse(e.dataTransfer?.getData("application/json") || "");
  } catch {
    console.warn("Invalid breadcrumb drop data");
    dragOverPath.value = null;
    return;
  }

  if (!data?.name) {
    dragOverPath.value = null;
    return;
  }

  const correct_name = data.is_dir
    ? `${joinPath(useFSStore().currentPath, data.name)}/`
    : joinPath(useFSStore().currentPath, data.name);

  await action.move(correct_name, path);

  dragOverPath.value = null;
}
</script>

<template>
  <ClientOnly>
    <Transition name="slide-fade" appear>
      <div v-if="!isMobile">
        <LazyUBreadcrumb
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
            <LazyULink
              class="mx-0 px-2 py-1 rounded-md hover:bg-elevated truncate max-w-40"
              :class="{
                'border-2 border-neutral': dragOverPath === item.path,
                'hover:bg-elevated': dragOverPath !== item.path,
              }"
              :title="item.label"
              @click="handleClick(item.path)"
              @dragover.prevent="onDragOverCrumb($event, item.path)"
              @dragleave="onDragLeaveCrumb"
              @drop.prevent="onDropCrumb($event, item.path)"
            >
              {{ item.label }}
            </LazyULink>
          </template>
        </LazyUBreadcrumb>
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
