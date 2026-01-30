<script lang="ts" setup>
import type { TerminalBlock } from "~~/shared/types/terminal_types";

const props = defineProps<{ block: TerminalBlock }>();

const levelClassMap = {
  default: "text-gray-300",
  info: "text-blue-400",
  success: "text-green-400",
  warning: "text-yellow-400",
  error: "text-red-500",
  muted: "text-gray-500",
};
</script>

<template>
  <div>
    <pre
      class="text-sm whitespace-pre-wrap"
      :class="levelClassMap[block.level ?? 'default']"
      v-text="props.block.content"
    />
  </div>
</template>
