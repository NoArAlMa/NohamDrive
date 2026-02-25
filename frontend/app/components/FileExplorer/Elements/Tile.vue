<script lang="ts" setup>
import type { ApiFileItem } from "~~/shared/types/file_tree";
import { useFileRenameRegistry } from "~/composables/file/RenameRegistry";

const { register, unregister } = useFileRenameRegistry();
const FSStore = useFSStore();

const props = defineProps<{
  item: ApiFileItem;
  selected: boolean;
}>();

const emit = defineEmits<{
  (e: "update:selected", item: ApiFileItem, checked: boolean): void;
}>();

const action = useFsActions();
const key = computed(() => joinPath(FSStore.currentPath, props.item.name));

watch(
  key,
  (newKey, oldKey) => {
    if (oldKey) unregister(oldKey);
    register(newKey, startEditing);
  },
  { immediate: true },
);

const isEditing = ref(false);
const isSubmitting = ref(false);
const baseName = ref("");
const extension = ref("");
const inputRef = ref<HTMLInputElement | null>(null);
const error = ref<string | null>(null);

onBeforeUnmount(() => {
  unregister(key.value);
});

function startEditing() {
  isEditing.value = true;

  if (props.item.is_dir) {
    baseName.value = props.item.name;
    extension.value = "";
  } else {
    const { base, ext } = splitFilename(props.item.name);
    baseName.value = base;
    extension.value = ext;
  }

  nextTick(() => {
    inputRef.value?.focus();
    inputRef.value?.select();
  });
}

async function submitEditing() {
  if (isSubmitting.value) return;
  isSubmitting.value = true;

  const newName = props.item.is_dir
    ? baseName.value
    : baseName.value + extension.value;

  if (!newName || newName === props.item.name) {
    cancelEditing();
    isSubmitting.value = false;
    return;
  }

  try {
    await action.rename(props.item.name, newName, props.item);
    isEditing.value = false;
  } catch (e) {
    error.value = "Erreur lors du renommage";
  } finally {
    isSubmitting.value = false;
  }
}

const cancelEditing = () => {
  isEditing.value = false;
};

function open() {
  action.open(props.item);
}

const isHovered = ref(false);

const isChecked = computed({
  get: () => props.selected,
  set: (val: boolean) => emit("update:selected", props.item, val),
});

const tileRef = ref<HTMLDivElement>();

onLongPress(
  tileRef,
  () => {
    isChecked.value ? (isChecked.value = false) : (isChecked.value = true);
  },
  {
    delay: 300,
  },
);

function onDragStart(e: DragEvent) {
  if (!e.dataTransfer) return;

  const payload = {
    name: props.item.name,
    is_dir: props.item.is_dir,
    path: joinPath(FSStore.currentPath, props.item.name),
  };

  e.dataTransfer.effectAllowed = "move";
  e.dataTransfer.setData("application/json", JSON.stringify(payload));
}

const isDragOver = ref(false);

function onDragOver(e: DragEvent) {
  if (!props.item.is_dir) return;
  e.preventDefault();
  e.dataTransfer!.dropEffect = "move";
  isDragOver.value = true;
}

function onDragLeave() {
  isDragOver.value = false;
}

async function onDrop(e: DragEvent) {
  if (!props.item.is_dir || !e.dataTransfer) return;

  e.preventDefault();

  let data: {
    name: string;
    path: string;
    is_dir: boolean;
  } | null = null;

  try {
    data = JSON.parse(e.dataTransfer.getData("application/json"));
  } catch {
    console.warn("Invalid drag data");
    isDragOver.value = false;
    return;
  }

  if (!data?.path) {
    isDragOver.value = false;
    return;
  }

  const destinationPath = props.item.is_dir
    ? joinPath(FSStore.currentPath, props.item.name) + "/"
    : joinPath(FSStore.currentPath, props.item.name);

  const correct_path = data.is_dir
    ? joinPath(FSStore.currentPath, data.name) + "/"
    : joinPath(FSStore.currentPath, data.name);

  if (correct_path === destinationPath) {
    isDragOver.value = false;
    return;
  }

  await action.move(correct_path, destinationPath);

  isDragOver.value = false;
}
</script>

<template>
  <FileExplorerContextMenu :row="props.item">
    <section class="w-35 h-35">
      <div
        class="relative flex flex-col items-center justify-between p-4 w-full h-full rounded-lg cursor-pointer transition-all duration-150 select-none hover:bg-muted/50 hover:shadow-sm group"
        :class="{
          'border-2 border-neutral ': isDragOver,
          'shadow-sm bg-muted/50': isChecked,
        }"
        @mouseenter="isHovered = true"
        @mouseleave="isHovered = false"
        @dblclick="open"
        draggable="true"
        @dragstart="onDragStart"
        @dragover="onDragOver"
        @drop.prevent="onDrop"
        @dragleave="onDragLeave"
        ref="tileRef"
      >
        <div
          class="absolute top-1 left-1 transition-opacity"
          :class="{
            'opacity-100': isHovered || isChecked,
            'opacity-0': !isHovered && !isChecked,
          }"
        >
          <UCheckbox
            v-model="isChecked"
            :ui="{
              base: 'rounded-full',
            }"
          />
        </div>
        <div class="flex items-center justify-center">
          <UIcon
            v-if="item.is_dir"
            name="fxemoji:filefolder"
            class="size-16 shrink-0 mb-2"
          />
          <UIcon
            v-else
            :name="getFileIcon(item.name)"
            class="size-16 shrink-0 mb-2"
          />
        </div>

        <div class="truncate w-full flex items-center justify-center">
          <template v-if="!isEditing">
            <span
              class="text-sm text-center truncate w-full"
              :title="item.name"
            >
              {{ item.name }}
            </span>
          </template>

          <template v-else>
            <div
              class="flex items-center justify-center w-full"
              :aria-hidden="false"
            >
              <LazyUInput
                ref="inputRef"
                v-model="baseName"
                size="md"
                variant="none"
                :highlight="true"
                :ui="{ base: 'h-6' }"
                class="w-auto"
                :loading="isSubmitting"
                @keydown.enter.prevent="submitEditing"
                @keydown.esc="cancelEditing"
                @blur.prevent="cancelEditing"
              />
            </div>
          </template>
        </div>
      </div>
    </section>
  </FileExplorerContextMenu>
</template>
