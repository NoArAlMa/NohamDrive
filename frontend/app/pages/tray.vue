<script lang="ts" setup>
definePageMeta({
  layout: false,
  middleware: "electron-middleware",
});
</script>

<template>
  <UApp>
    <section
      class="w-full h-screen flex flex-col items-center justify-center gap-3 px-3 text-center select-none"
    >
      <!-- Icône -->
      <div class="text-3xl">🚧</div>

      <!-- Titre -->
      <h1 class="text-md font-semibold">Bientôt dispo</h1>

      <!-- Texte court -->
      <p class="text-sm text-gray-500 leading-tight">
        Feature en cours de dev…
      </p>

      <!-- Mini loader -->
      <div class="flex gap-1 mt-1 rounded-full bg-gray-800 py-2 px-1.5">
        <span
          class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]"
        />
        <span
          class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:100ms]"
        />
        <span
          class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:200ms]"
        />
      </div>
    </section>
  </UApp>
</template>
