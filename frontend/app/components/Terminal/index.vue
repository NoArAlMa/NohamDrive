<script setup lang="ts">
const { currentPath } = useFSStore();
const { blocks, currentInput, submit } = useTerminal();

const input = ref<HTMLInputElement | null>(null);

function focusInput() {
  input.value?.focus();
}

const bottom = ref<HTMLElement | null>(null);

watch(
  blocks,
  async () => {
    await nextTick();
    bottom.value?.scrollIntoView({ behavior: "smooth" });
  },
  { deep: true },
);
</script>

<template>
  <div
    class="h-full overflow-y-auto bg-[#0d1117] p-4 font-mono text-sm text-gray-300"
    @click="focusInput"
  >
    <!-- History -->
    <div
      v-for="(block, index) in blocks"
      :key="index"
      class="mb-1 whitespace-pre-wrap"
    >
      <!-- Output -->
      <TerminalOutputBlock v-if="block.type === 'output'" :block="block" />

      <!-- Command echo -->
      <div v-else class="flex items-center gap-1">
        <span class="text-blue-400">ND:{{ currentPath }} $ </span>
        <span>{{ block.content }}</span>
      </div>
    </div>

    <div ref="bottom" />

    <!-- Active input -->
    <div class="flex items-center gap-1">
      <span class="text-blue-400"> ND:{{ currentPath }} $ </span>
      <input
        ref="input"
        v-model="currentInput"
        @keydown.enter.prevent="submit"
        class="flex-1 bg-transparent outline-none caret-blue-400"
        autocomplete="off"
        spellcheck="false"
      />
    </div>
  </div>
</template>
