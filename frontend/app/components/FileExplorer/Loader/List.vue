<script lang="ts" setup></script>

<template>
  <div class="space-y-2 px-4 py-3">
    <div v-for="i in 6" :key="i" class="flex items-center gap-2">
      <USkeleton class="h-15 w-full rounded-md" />
    </div>
  </div>
</template>
