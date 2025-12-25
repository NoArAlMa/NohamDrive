<script lang="ts" setup></script>

<template>
  <section class="flex flex-col h-screen w-screen overflow-hidden">
    <div class="shrink-0 p-2 border-b">
      <FileExplorerBreadcrumb />
    </div>

    <!-- IMPORTANT : flex-1 + overflow-hidden -->
    <div class="flex-1 overflow-hidden">
      <FileExplorer />
    </div>
  </section>
</template>
