<script setup lang="ts">
import type { SelectItem } from "@nuxt/ui";

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

const modelValue = defineModel<"tiles" | "list">();

const currentIcon = computed(
  () => items.find((i) => i.value === modelValue.value)?.icon,
);
</script>

<template>
  <USelect
    v-model="modelValue"
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
