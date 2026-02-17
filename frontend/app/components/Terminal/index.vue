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

const history = ref<string[]>([]);
let historyIndex = ref(-1); // -1 = rien sélectionné dans l'historique
let draft = "";

async function submitCommand() {
  const value = currentInput.value.trim();
  if (!value || commandLoading.value) return;

  commandLoading.value = true;

  // Enregistrer dans l'historique si nouveau
  if (
    !history.value.length ||
    history.value[history.value.length - 1] !== value
  ) {
    history.value.push(value);
  }

  historyIndex.value = -1;
  draft = "";

  await submit();

  currentInput.value = "";
  commandLoading.value = false;

  // Scroll automatique
  await nextTick();
  bottom.value?.scrollIntoView({ behavior: "smooth" });
}

// Naviguer dans l'historique
function navigateUp() {
  if (!history.value.length) return;

  if (historyIndex.value === -1) {
    draft = currentInput.value; // sauvegarde le draft actuel
    historyIndex.value = history.value.length - 1;
  } else if (historyIndex.value > 0) {
    historyIndex.value--;
  }

  const value = history.value[historyIndex.value];
  if (value !== undefined) {
    currentInput.value = value;
  }
}

function navigateDown() {
  if (historyIndex.value === -1) return;

  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++;
    const value = history.value[historyIndex.value];
    if (value !== undefined) {
      currentInput.value = value;
    }
  } else {
    historyIndex.value = -1;
    currentInput.value = draft; // remet le draft
  }
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
    class="h-screen overflow-y-auto bg-(--terminal) p-4 font-terminal text-sm text-gray-300"
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
      <!-- Progress -->
      <TerminalProgressBlock
        v-else-if="block.type === 'progress'"
        :block="block"
      />
      <!-- Command echo -->
      <div v-else-if="block.type === 'command'" class="flex items-center gap-1">
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
        @keydown.up.prevent="navigateUp"
        @keydown.down.prevent="navigateDown"
      />
    </section>
  </div>
</template>
