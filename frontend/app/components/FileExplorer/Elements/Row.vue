<script lang="ts" setup>
import type { TableRow } from "@nuxt/ui";
import { useFileRenameRegistry } from "~/composables/file/RenameRegistry";
import { useDebounceFn, useDraggable, useDropZone } from "@vueuse/core";
import { onLongPress } from "@vueuse/core";

// Ce composant reçoit une prop "row" qui représente une ligne du tableau (un fichier ou un dossier).
const props = defineProps<{ row: TableRow<ApiFileItem> }>();

const { isMobile } = useResponsive();

// On utilise un composable maison pour enregistrer/désenregistrer les fonctions de renommage.
// Cela permet de déclencher l'édition depuis n'importe où (ex: menu contextuel).
const { register, unregister } = useFileRenameRegistry();

const action = useFsActions();
const FSStore = useFSStore();
const isEditing = ref(false);
const isSubmitting = ref(false);
const baseName = ref("");
const extension = ref("");
const inputRef = ref<HTMLInputElement | null>(null);
const rowRef = ref<HTMLElement | null>(null);

const key = computed(() =>
  joinPath(FSStore.currentPath, props.row.original.name),
);
const error = ref<string | null>(null);

// Quand la clé change (ex: on change de dossier), on met à jour l'enregistrement.
// Cela permet de savoir quelle fonction appeler pour éditer ce fichier/dossier.
watch(
  key,
  (newKey, oldKey) => {
    if (oldKey) unregister(oldKey);
    register(newKey, startEditing);
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  unregister(key.value);
});

function startEditing() {
  isEditing.value = true; // On passe en mode édition.

  // Si c'est un dossier, on prend le nom tel quel (pas d'extension).
  if (props.row.original.is_dir) {
    baseName.value = props.row.original.name;
    extension.value = "";
  } else {
    const { base, ext } = splitFilename(props.row.original.name);
    baseName.value = base;
    extension.value = ext;
  }
}

// Appelée quand on appuie sur Entrée ou que l'input perd le focus.
async function submitEditing() {
  // Si une requête est déjà en cours, on ne fait rien.
  if (isSubmitting.value) return;
  isSubmitting.value = true;

  const newName = props.row.original.is_dir
    ? baseName.value
    : baseName.value + extension.value;

  if (!newName || newName === props.row.original.name) {
    cancelEditing();
    isSubmitting.value = false;
    return;
  }

  try {
    await action.rename(props.row.original.name, newName, props.row.original);
  } catch (e) {
    error.value = "Erreur lors du renommage";
    console.error(e);
  } finally {
    isSubmitting.value = false;
    if (!error.value) isEditing.value = false;
  }
}

onLongPress(
  rowRef,
  () => {
    if (!isMobile.value) return;

    props.row.toggleSelected?.();
  },
  {
    delay: 400,
  },
);

const cancelEditing = useDebounceFn(() => {
  isEditing.value = false;
}, 100);

function onRowClick() {
  if (!props.row) return;

  props.row.toggleSelected?.();
}

function onDragStart(e: DragEvent) {
  if (!e.dataTransfer) return;

  const payload = {
    name: props.row.original.name,
    is_dir: props.row.original.is_dir,
    path: joinPath(FSStore.currentPath, props.row.original.name),
  };

  e.dataTransfer.effectAllowed = "move";
  e.dataTransfer.setData("application/json", JSON.stringify(payload));
}

const isDragOver = ref(false);

function onDragOver(e: DragEvent) {
  if (!props.row.original.is_dir) return;
  e.preventDefault();
  e.dataTransfer!.dropEffect = "move";
  isDragOver.value = true;
}

function onDragLeave() {
  isDragOver.value = false;
}

async function onDrop(e: DragEvent) {
  if (!props.row.original.is_dir || !e.dataTransfer) return;

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

  const destinationPath = props.row.original.is_dir
    ? joinPath(FSStore.currentPath, props.row.original.name) + "/"
    : joinPath(FSStore.currentPath, props.row.original.name);

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
  <div
    class="relative max-w-64 py-4 rounded-sm flex items-center group"
    :aria-hidden="false"
    @dblclick="!isMobile && onRowClick"
    ref="rowRef"
    :class="{ 'border-2 border-neutral ': isDragOver }"
    draggable="true"
    @dragstart="onDragStart"
    @dragover="onDragOver"
    @drop.prevent="onDrop"
    @dragleave="onDragLeave"
  >
    <!-- Icone dossier ou fichier -->
    <LazyUIcon
      draggable="false"
      v-if="row.original.is_dir"
      name="heroicons-folder"
      class="text-lg mr-2 shrink-0"
    />
    <LazyUIcon
      draggable="false"
      v-else
      :name="getFileIcon(row.original.name)"
      class="text-lg mr-2 shrink-0"
      :alt="`Icon for ${row.original.name}`"
    />

    <!-- Nom du fichier -->
    <LazyULink draggable="false" v-if="!isEditing" class="min-w-0">
      <span
        draggable="false"
        class="block truncate hover:underline underline-offset-2 cursor-pointer"
        @click="action.open(props.row.original)"
        :title="row.getValue('name')"
      >
        {{ row.getValue("name") }}
      </span>
    </LazyULink>
    <div
      v-else
      class="relative h-full flex items-center group"
      :aria-hidden="false"
    >
      <LazyUInput
        ref="inputRef"
        v-model="baseName"
        variant="none"
        :highlight="true"
        color="neutral"
        size="md"
        class="w-auto"
        :ui="{ base: 'h-6' }"
        :loading="isSubmitting"
        autofocus
        @keydown.enter.prevent="submitEditing"
        @keydown.esc="cancelEditing"
        @blur.prevent="cancelEditing"
      />
      <span
        v-if="!row.original.is_dir && extension"
        class="text-gray-400 select-none ml-0.5"
      >
        {{ extension }}
      </span>
    </div>
  </div>
</template>
