<script setup lang="ts">
const fsStore = useFSStore();
const { currentPath } = storeToRefs(fsStore);
const { blocks, currentInput, submit } = useTerminal();

const input = ref<HTMLInputElement | null>(null);

function focusInput() {
  input.value?.focus();
}

const bottom = ref<HTMLElement | null>(null);

const commandLoading = ref(false);

async function submitCommand() {
  commandLoading.value = true;

  await submit();

  commandLoading.value = false;
}

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
    class="h-screen overflow-y-auto bg-[#0d1117] p-4 font-mono text-sm text-gray-300"
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
        <span class="text-blue-400">ND:{{ block.cwd }} $</span>
        <span>{{ block.content }}</span>
      </div>
    </div>

    <div ref="bottom" />

    <!-- Active input -->
    <section class="flex items-center gap-1">
      <UIcon
        name="material-symbols:progress-activity"
        class="animate-spin mr-2"
        v-if="commandLoading"
      />
      <span class="text-blue-400">ND:{{ currentPath }} $ </span>

      <input
        ref="input"
        v-model="currentInput"
        @keydown.enter.prevent="submitCommand"
        class="flex-1 bg-transparent outline-none caret-blue-400"
        autocomplete="off"
        spellcheck="false"
      />
    </section>
  </div>
</template>
