<script lang="ts" setup>
import type { OutputBlock } from "~~/shared/types/terminal_types";

const props = defineProps<{ block: OutputBlock }>();

const levelClassMap: Record<string, string> = {
  default: "",
  info: "text-info",
  success: "text-success",
  warning: "text-warning",
  error: "text-error",
  muted: "text-gray-500",
};
</script>

<template>
  <div>
    <pre
      class="text-sm whitespace-pre-wrap font-terminal"
      :class="levelClassMap[(props.block as any).level ?? 'default']"
      v-text="props.block.content"
    />
  </div>
</template>
