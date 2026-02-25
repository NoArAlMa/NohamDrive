<script setup lang="ts">
import type { FileColumn } from "~/composables/useFileExplorerSettings";

const { availableColumns, visibleColumns } = useFileExplorerSettings();

const selectValue = computed({
  get: () =>
    availableColumns.filter((col) => visibleColumns.value.includes(col.value)),
  set: (val: { label: string; value: FileColumn }[]) => {
    visibleColumns.value = val.map((v) => v.value);
  },
});
</script>

<template>
  <USelectMenu
    v-model="selectValue"
    :items="availableColumns"
    multiple
    :search-input="false"
    leading-icon="material-symbols:combine-columns-outline-rounded"
    value-attribute="value"
    option-attribute="label"
    placeholder="Columns"
    :arrow="true"
    :ui="{
      trailingIcon:
        'group-data-[state=open]:rotate-180 transition-transform duration-200',
    }"
    class="w-fit shadow-md"
  >
    <template #default>Columns</template>
  </USelectMenu>
</template>
