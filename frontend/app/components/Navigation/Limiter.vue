<script lang="ts" setup>
const used = ref(750);
const max = ref(1000);

const Percent = ref((used.value / max.value) * 100);
</script>

<template>
  <section
    class="flex flex-col w-full py-3 px-2 rounded-md bg-neutral-800/40 hover:bg-neutral-800/45"
  >
    <div class="mb-2">
      <h1 class="text-sm font-bold">Storage</h1>
    </div>
    <div class="w-full flex items-center justify-center">
      <UProgress v-model="Percent" color="primary" size="sm" :max="100" />
    </div>
    <div>
      <span class="text-sm">
        <strong class="text-primary font-medium">{{ used }} MB</strong> used of
        <strong>1 GB</strong></span
      >
    </div>
  </section>
</template>
