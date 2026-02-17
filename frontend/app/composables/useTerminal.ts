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

  const sortedCommands = Object.keys(commandRegistry).sort();

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

  const ghostText = computed(() => {
    const input = currentInput.value;
    if (!input) return "";

    const token = getLastTokenInfo(input);

    const trimmed = input.trimStart();
    const firstSpaceIndex = trimmed.indexOf(" ");

    const isTypingCommand = firstSpaceIndex === -1 && !input.endsWith(" ");

    if (isTypingCommand) {
      const partial = token.value;

      const match = sortedCommands.find(
        (cmd) => cmd.startsWith(partial) && cmd !== partial,
      );

      if (!match) return "";

      return match.slice(partial.length);
    }
    const fileTreeStore = useFileTree();

    const sortedFileNames = computed(() =>
      [...fileTreeStore.fileTree.map((f) => f.name)].sort(),
    );
    const match = sortedFileNames.value.find((name) =>
      token.value ? name.startsWith(token.value) && name !== token.value : true,
    );

    if (!match) return "";

    return match.slice(token.value.length);
  });

  function getLastTokenInfo(input: string) {
    const single = (input.match(/'/g) || []).length;
    const double = (input.match(/"/g) || []).length;

    const inSingle = single % 2 !== 0;
    const inDouble = double % 2 !== 0;

    if (inSingle || inDouble) {
      const quote = inSingle ? "'" : '"';
      const start = input.lastIndexOf(quote) + 1;
      return { start, end: input.length, value: input.slice(start), quote };
    }

    const lastSpace = input.lastIndexOf(" ");
    return {
      start: lastSpace + 1,
      end: input.length,
      value: input.slice(lastSpace + 1),
      quote: null,
    };
  }

  function applySuggestion() {
    const input = currentInput.value;
    if (!ghostText.value) return;

    const token = getLastTokenInfo(input);

    const before = input.slice(0, token.start);
    let completed = token.value + ghostText.value;

    if (!token.quote && completed.includes(" ")) {
      completed = `"${completed}"`;
    }

    let result = before + completed;

    if (token.quote) {
      result = before + completed;
    }

    currentInput.value = result;
  }

  async function submit() {
    const value = currentInput.value.trim();
    if (!value) return;

    const fileTreeStore = useFileTree();
    const { currentPath } = useFSStore();

    // On attend que FileTree soit chargé
    if (fileTreeStore.fileTree.length === 0) {
      await until(() => fileTreeStore.loading).toBe(false);
    }

    const context = {
      fileTree: fileTreeStore.fileTree,
      currentPath: currentPath,
    };

    const parsed = parseCommand(value);

    if (!parsed.command) {
      blocks.value.push({ type: "command", content: value, cwd: currentPath });
      blocks.value.push({
        type: "output",
        level: "error",
        content: `${parsed.name}: command not found`,
      });
      reset();
      return;
    }

    const result = await parsed.command.run(parsed.args, context);

    blocks.value.push({ type: "command", content: value, cwd: currentPath });

    if (Array.isArray(result)) {
      result.forEach((item) => {
        if (item.type !== "nope") {
          if (item.type === "clear") {
            blocks.value = [];
          } else {
            blocks.value.push(item);
          }
        }
      });
    } else if (result) {
      if (result.type === "clear") {
        blocks.value = [];
      } else if (result.type !== "nope") {
        blocks.value.push(result);
      }
    }

    reset();
  }

  function reset() {
    currentInput.value = "";
    nextTick(() => inputRef?.value?.focus());
  }

  return { blocks, currentInput, submit, applySuggestion, ghostText };
}
