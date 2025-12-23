<script lang="ts" setup></script>

<template>
  <section class="flex flex-col h-full min-h-0">
    <div class="shrink-0 p-2 border-b">
      <FileExplorerBreadcrumb />
    </div>

    <div class="flex-1 min-h-0 overflow-auto">
      <FileExplorer class="h-full" />
    </div>

    <div class="shrink-0 p-2 border-t">
      <h1>This is the footer</h1>
    </div>
  </section>
</template>
