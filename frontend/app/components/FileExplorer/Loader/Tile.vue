<template>
  <div
    class="grid grid-cols-[repeat(auto-fill,minmax(140px,1fr))] auto-rows-min content-baseline justify-items-center gap-4 p-4 h-full w-full"
  >
    <div v-for="i in 20" :key="i">
      <USkeleton class="h-35 w-35 rounded-md" />
    </div>
  </div>
</template>
