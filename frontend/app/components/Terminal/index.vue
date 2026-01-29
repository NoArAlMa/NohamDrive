<script setup lang="ts">
const { currentPath } = useFSStore();
const { blocks, currentInput, submit } = useTerminal();

const input = ref<HTMLInputElement>();

function focusInput() {
  input.value?.focus();
}
</script>

<template>
  <div class="terminal" @click="focusInput">
    <div v-for="(block, index) in blocks" :key="index" class="block">
      <TerminalOutputBlock
        v-if="block.type === 'output'"
        :content="block.content"
      />

      <TerminalErrorBlock
        v-if="block.type === 'error'"
        :content="block.content"
      />

      <!-- Command echo -->
      <div v-else-if="block.type === 'command'" class="command">
        <span class="prompt">ND:{{ currentPath }} $</span>{{ block.content }}
      </div>
    </div>

    <!-- Active input (always last) -->
    <div class="input-line">
      <span class="prompt">ND:{{ currentPath }} $</span>
      <input
        ref="input"
        v-model="currentInput"
        @keydown.enter.prevent="submit"
        class="input"
        autocomplete="off"
      />
    </div>
  </div>
</template>

<style scoped>
.terminal {
  background: #0d1117;
  color: #c9d1d9;
  font-family: monospace;
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}

.block {
  margin-bottom: 6px;
}

.prompt {
  color: #58a6ff;
  margin-right: 4px;
}

.command {
  color: #c9d1d9;
}

.input-line {
  display: flex;
  align-items: center;
}

.input {
  background: transparent;
  border: none;
  outline: none;
  color: inherit;
  font-family: inherit;
  flex: 1;
}
</style>
