import type {
  TerminalBlock,
  TerminalCommand,
} from "~~/shared/types/terminal_types";
import { commandRegistry } from "./commands";

function parseArgs(input: string): string[] {
  const regex = /"([^"]*)"|'([^']*)'|(\S+)/g;
  const args: string[] = [];
  let match;

  while ((match = regex.exec(input)) !== null) {
    const arg = match[1] ?? match[2] ?? match[3];
    if (typeof arg === "string") {
      args.push(arg);
    }
  }

  return args;
}

export function useTerminal(inputRef?: any) {
  const blocks = ref<TerminalBlock[]>([]);
  const currentInput = ref("");

  function parseCommand(input: string): {
    name: string;
    command?: TerminalCommand;
    args: string[];
  } {
    const parts = parseArgs(input);

    const name = parts[0] ?? "";
    const args = parts.slice(1);

    const command =
      name && name in commandRegistry
        ? commandRegistry[name as keyof typeof commandRegistry]
        : undefined;

    return { name, command, args };
  }

  async function submit() {
    const value = currentInput.value.trim();
    if (!value) return;

    const fileTreeStore = useFileTree();
    const { currentPath } = useFSStore();

    const context = {
      fileTree: fileTreeStore.fileTree.value,
      currentPath: currentPath,
    };

    blocks.value.push({ type: "command", content: value, cwd: currentPath });

    const parsed = parseCommand(value);

    if (!parsed.command) {
      blocks.value.push({
        type: "output",
        level: "error",
        content: `${parsed.name}: command not found`,
      });
      reset();
      return;
    }

    const result = await parsed.command.run(parsed.args, context);

    if (result && result.type === "clear") {
      blocks.value = [];
    } else if (result) {
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
