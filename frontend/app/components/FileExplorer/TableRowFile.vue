<script lang="ts" setup>
import type { TableRow } from "@nuxt/ui";
import { useFileRenameRegistry } from "~/composables/file/RenameRegistry";
import { onClickOutside, useDebounceFn } from "@vueuse/core";

// Ce composant reçoit une prop "row" qui représente une ligne du tableau (un fichier ou un dossier).
const props = defineProps<{ row: TableRow<ApiFileItem> }>();

// On utilise un composable maison pour enregistrer/désenregistrer les fonctions de renommage.
// Cela permet de déclencher l'édition depuis n'importe où (ex: menu contextuel).
const { register, unregister } = useFileRenameRegistry();

// On utilise un composable pour les actions sur les fichiers (ex: renommer, ouvrir).
const action = useFsActions();

// On accède au store global pour gérer l'état de l'explorateur de fichiers.
const FSStore = useFSStore();

// isEditing : Indique si on est en train de renommer le fichier/dossier.
const isEditing = ref(false);

// isSubmitting : Indique si une requête de renommage est en cours (pour éviter les doubles clics).
const isSubmitting = ref(false);

// baseName : Stocke le nom de base du fichier/dossier (sans extension).
const baseName = ref("");

// extension : Stocke l'extension du fichier (ex: ".txt", ".pdf").
const extension = ref("");

// inputRef : Référence vers l'input pour le focus et la sélection automatique.
const inputRef = ref<HTMLInputElement | null>(null);

// On génère une clé unique pour chaque fichier/dossier, basée sur son chemin complet.
const key = computed(() =>
  joinPath(FSStore.currentPath, props.row.original.name)
);

// Quand la clé change (ex: on change de dossier), on met à jour l'enregistrement.
// Cela permet de savoir quelle fonction appeler pour éditer ce fichier/dossier.
watch(
  key,
  (newKey, oldKey) => {
    if (oldKey) unregister(oldKey);
    register(newKey, startEditing);
  },
  { immediate: true }
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

  // On attend que l'input soit rendu, puis on le focus et on sélectionne tout son contenu.
  nextTick(() => {
    setTimeout(() => {
      const input = inputRef?.value;
      input?.focus;
      input?.select;
    }, 50);
  });
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
  } finally {
    // Dans tous les cas, on réinitialise l'état.
    isSubmitting.value = false;
    isEditing.value = false;
  }
}

const cancelEditing = useDebounceFn(() => {
  isEditing.value = false;
}, 100);

function onRowClick() {
  if (!props.row) return;
  try {
    props.row.toggleSelected?.();
  } catch (e) {
    console.log("lala");
  }
}
</script>

<template>
  <div
    class="relative h-full flex items-center group"
    :aria-hidden="false"
    @click="onRowClick"
    @dblclick="action.open(props.row.original)"
  >
    <!-- Icone dossier ou fichier -->
    <UIcon
      v-if="row.original.is_dir"
      name="heroicons-folder"
      class="text-lg mr-2"
    />
    <UIcon
      v-else
      :name="getFileIcon(row.original.name)"
      class="text-lg mr-2"
      :alt="`Icon for ${row.original.name}`"
    />

    <!-- Nom du fichier -->
    <ULink v-if="!isEditing">
      <span
        class="hover:underline underline-offset-2 cursor-pointer"
        @click="action.open(props.row.original)"
      >
        {{ row.getValue("name") }}
      </span>
    </ULink>
    <div
      v-else
      class="relative h-full flex items-center group"
      :aria-hidden="false"
    >
      <UInput
        ref="inputRef"
        v-model="baseName"
        variant="none"
        :highlight="true"
        color="neutral"
        size="md"
        class="w-auto"
        :ui="{ base: 'h-6' }"
        autofocus
        @keydown.enter.prevent="submitEditing"
        @keydown.esc="cancelEditing"
        @blur="cancelEditing"
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
