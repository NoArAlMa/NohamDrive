<script lang="ts" setup>
const { createFolder } = useFsActions();

const newFolderName = ref("");
const error = ref<string | undefined>();

const emit = defineEmits<{ close: [any] }>();

function close() {
  emit("close", "");
}

async function confirmCreateFolder() {
  if (!newFolderName.value.trim()) {
    error.value = "Le nom du dossier est requis.";
    return;
  }

  const { success, message } = await createFolder(newFolderName.value.trim());
  if (success) {
    close();
  } else {
    error.value = message;
  }
}
</script>

<template>
  <UModal
    title="Nouveau dossier"
    description="Formulaire pour créer un nouveau dossier"
  >
    <template #content>
      <UCard class="flex flex-col gap-2 justify-between">
        <div class="w-full flex flex-row gap-2 items-center mb-10">
          <UIcon
            name="material-symbols:create-new-folder-outline"
            class="size-6"
          />
          <h3 class="text-2xl font-semibold">Nouveau dossier</h3>
        </div>
        <UFormField class="space-y-2" label="Nom du dossier" :error="error">
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
            @click="close"
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
