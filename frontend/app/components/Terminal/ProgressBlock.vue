<script setup lang="ts">
import type { ProgressBlock } from "~~/shared/types/terminal_types";

const props = defineProps<{
  block: ProgressBlock;
}>();
console.info(props.block.total);
const percent = computed(() => {
  if (props.block.total === 0) return 0;
  return Math.floor((props.block.loaded / props.block.total) * 100);
});

const barColor = computed(() => {
  switch (props.block.status) {
    case "success":
      return "success";
    case "error":
      return "error";
    default:
      return "primary";
  }
});
</script>

<template>
  <div class="flex items-center gap-3 text-sm">
    <span class="truncate w-48">
      {{ block.subject }}
    </span>
    <div v-if="!props.block.loaded" class="flex gap-1 flex-row items-center">
      <UProgress :color="barColor" v-model="percent" class="w-5xl" />

      <span class="w-12 text-right tabular-nums font-sans">
        {{ percent }} %
      </span>
    </div>
    <div v-if="props.block.loaded" class="flex items-center">
      <UIcon
        v-if="props.block.status === 'error'"
        name="material-symbols:close-rounded"
        class="text-red-500"
      />
      <UIcon
        v-else
        name="material-symbols:check-rounded"
        class="text-green-500"
      />
    </div>
  </div>
</template>
