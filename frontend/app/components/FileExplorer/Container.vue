<script lang="ts" setup>
const selectedCount = ref(0);
</script>

<template>
  <section class="flex flex-col h-screen w-screen overflow-hidden">
    <div class="shrink-0 p-2 border-b">
      <FileExplorerBreadcrumb />
    </div>

    <!-- IMPORTANT : flex-1 + overflow-hidden -->
    <div class="flex-1 overflow-hidden">
      <ClientOnly>
        <FileExplorer v-model:selectedCount="selectedCount" />
      </ClientOnly>
    </div>

    <div>
      <FileExplorerFooter :selected-count="selectedCount" />
    </div>
  </section>
</template>
