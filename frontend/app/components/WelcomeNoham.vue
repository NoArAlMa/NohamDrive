<script lang="ts" setup>
const count = ref(0);
</script>

<template>
  <section class="w-screen h-screen flex flex-col justify-center items-center">
    <h1 class="text-6xl font-bold m-2 shadow-lg">Bienvenue Noham</h1>
    <p class="text-green-300 shadow">
      Installe toi et prends ton clavier pour admirer la beauté de notre
      invention
    </p>
    <div class="mt-5 flex justify-center items-center gap-5">
      <UButton
        icon="i-lucide-minus"
        variant="outline"
        size="sm"
        @click="count--"
      />
      <span :class="count < 0 ? 'text-red-600' : 'text-white'">
        {{ count }}
      </span>
      <UButton
        variant="outline"
        icon="i-lucide-plus"
        size="sm"
        @click="count++"
      />
    </div>
  </section>
</template>
