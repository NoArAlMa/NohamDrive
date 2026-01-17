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
</script>

<template>
  <UButton
    label="Créer dossier"
    @click="createFolder(randomWord())"
    variant="soft"
    color="neutral"
  />
</template>
