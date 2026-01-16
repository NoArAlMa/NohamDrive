<script lang="ts" setup>
function randomWord(length = 8): string {
  const chars = "abcdefghijklmnopqrstuvwxyz"; // lettres possibles
  let word = "";
  for (let i = 0; i < length; i++) {
    word += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return word;
}

async function createFolder() {
  const folderName = randomWord(6); // génère un nom aléatoire de 6 lettres
  await useFetch(`${useRuntimeConfig().public.apiBaseUrl}/storage/folder`, {
    method: "POST",
    body: {
      currentPath: useFSStore().currentPath,
      folderPath: folderName,
    },
  });
  useFileTree().retryFetching();
}
</script>

<template>
  <UButton
    label="Créer dossier"
    @click="createFolder"
    variant="soft"
    color="neutral"
  />
</template>
