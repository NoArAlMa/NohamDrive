// useTerminal.ts
import { ref, nextTick } from "vue";
import type { Block, TerminalCommand } from "~~/shared/types/terminal_types";
import { commandRegistry } from "./commands";

export function useTerminal(inputRef?: any) {
  const blocks = ref<Block[]>([]);
  const currentInput = ref("");

  function parseCommand(input: string): {
    command: TerminalCommand;
    args: string[];
  } | null {
    const parts = input.trim().split(" ");

    if (parts.length === 0) {
      return null;
    }

    const name = parts[0];
    const args = parts.slice(1);

    if (!name || !(name in commandRegistry)) {
      return null;
    }

    const command = commandRegistry[name as keyof typeof commandRegistry];

    return { command, args };
  }

  async function submit() {
    const value = currentInput.value.trim();
    if (!value) return;

    blocks.value.push({ type: "command", content: value });

    const parsed = parseCommand(value);
    if (!parsed) {
      blocks.value.push({
        type: "error",
        content: `Command not found: ${value}`,
      });
      reset();
      return;
    }

    const result = await parsed.command.run(parsed.args);

    if (result.type === "clear") {
      blocks.value = [];
    } else {
      blocks.value.push(result);
    }

    reset();
  }

  function reset() {
    currentInput.value = "";
    nextTick(() => inputRef?.value?.focus());
  }

  return { blocks, currentInput, submit };
}
