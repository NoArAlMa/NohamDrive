<script setup lang="ts">
import type { SelectItem } from "@nuxt/ui";

const { t } = useI18n();
const { viewMode } = useFileExplorerSettings();

type ViewMode = "tiles" | "list";

const items = computed<SelectItem[]>(() => [
  {
    label: t("fileExplorer.display.tiles") as string,
    value: "tiles",
    icon: "material-symbols:tile-small-outline-rounded",
  },
  {
    label: t("fileExplorer.display.list") as string,
    value: "list",
    icon: "material-symbols:format-list-bulleted-rounded",
  },
  {
    label: t("fileExplorer.display.compact") as string,
    value: "compact",
    icon: "material-symbols:list-rounded",
  },
]);

const currentIcon = computed(
  () => items.value.find((i) => i.value === viewMode.value)?.icon,
);
</script>

<template>
  <LazyUSelect
    v-model="viewMode"
    :items="items"
    value-key="value"
    :icon="currentIcon"
    class="size-9 shadow-sm"
    :content="{
      align: 'end',
      side: 'bottom',
      sideOffset: 8,
    }"
    :ui="{
      content: 'w-fit',
      trailingIcon:
        'group-data-[state=open]:rotate-180 transition-transform duration-200',
    }"
  />
</template>
