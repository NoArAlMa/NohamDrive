<script lang="ts" setup>
const { createFolder } = useFsActions();

function randomWord(length = 8): string {
  const chars = "abcdefghijklmnopqrstuvwxyz"; // lettres possibles
  let word = "";
  for (let i = 0; i < length; i++) {
    word += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return word;
}

const isModalOpen = ref(false);
const newFolderName = ref("");
const error = ref<string | undefined>();

function openModal() {
  newFolderName.value = "";
  error.value = undefined;
  isModalOpen.value = true;
}

async function confirmCreateFolder() {
  if (!newFolderName.value.trim()) {
    error.value = "Le nom du dossier est requis.";
    return;
  }

  const { success, message } = await createFolder(newFolderName.value.trim());
  if (success) {
    isModalOpen.value = false;
    error.value = undefined;
  } else {
    error.value = message; // Affiche l'erreur dans le formulaire
  }
}
</script>

<template>
  <UModal
    v-model:open="isModalOpen"
    title="Nouveau dossier"
    description="Formulaire pour créer un nouveau dossier"
  >
    <UButton
      label="Créer dossier"
      variant="soft"
      color="neutral"
      @click="openModal"
      :close-on-esc="true"
    />

    <template #content>
      <UCard class="flex flex-col gap-2 justify-between">
        <h3 class="text-2xl font-semibold mb-10">Nouveau dossier</h3>
        <UFormField class="space-y-2" label="Nom du fichier" :error="error">
          <UInput
            v-model="newFolderName"
            class=""
            placeholder="Nom du dossier"
            autofocus
            @keyup.enter="confirmCreateFolder"
          />
        </UFormField>

        <div class="flex justify-end gap-2">
          <UButton
            label="Annuler"
            variant="ghost"
            color="neutral"
            @click="isModalOpen = false"
          />
          <UButton
            label="Créer"
            color="primary"
            variant="subtle"
            loading-auto
            class="hover:cursor-pointer"
            :disabled="!newFolderName.trim()"
            @click="confirmCreateFolder"
          />
        </div>
      </UCard>
    </template>
  </UModal>
</template>
