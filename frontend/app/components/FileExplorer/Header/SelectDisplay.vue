<script setup lang="ts">
import type { SelectItem } from "@nuxt/ui";

const { viewMode } = useFileExplorerSettings();

type ViewMode = "tiles" | "list";

const items = [
  {
    label: "Tiles",
    value: "tiles",
    icon: "material-symbols:tile-small-outline-rounded",
  },
  {
    label: "List",
    value: "list",
    icon: "material-symbols:format-list-bulleted-rounded",
  },
] satisfies SelectItem[];

const currentIcon = computed(
  () => items.find((i) => i.value === viewMode.value)?.icon,
);
</script>

<template>
  <LazyUSelect
    v-model="viewMode"
    :items="items"
    value-key="value"
    :icon="currentIcon"
    class="size-9"
    :content="{
      align: 'end',
      side: 'bottom',
      sideOffset: 8,
    }"
    :ui="{
      content: 'w-fit',
    }"
  />
</template>
