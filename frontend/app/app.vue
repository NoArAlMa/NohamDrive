<script lang="ts" setup>
const count = ref(0);
</script>

<template>
  <section class="w-screen h-screen flex flex-col justify-center items-center">
    <h1 class="text-6xl font-bold m-2">Bienvenue Noham</h1>
    <p class="text-green-400">
      Installe toi et prends ton clavier pour admirer la beauté de notre
      invention
    </p>
    <div class="mt-5 flex justify-center items-center gap-5">
      <UButton icon="i-lucide-minus" size="sm" @click="count--" />
      <span>{{ count }}</span>
      <UButton icon="i-lucide-plus" size="sm" @click="count++" />
    </div>
  </section>
</template>
