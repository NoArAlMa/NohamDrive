import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";

export const listCommand: TerminalCommand = {
  name: "list",
  description: "List current files in dir",
  run: (args: string[], ctx?: TerminalContext) => {
    if (args.length === 0) {
      const files = Object.values(ctx?.fileTree ?? {}).map(
        (file) => `${file.is_dir ? "[DIR] " : ""}${file.name}`,
      );

      return {
        type: "output",
        content: `${files.join("\n")}`,
      };
    }
    return {
      type: "output",
      level: "error",
      content: "Usage: list (no arguments expected)",
    };
  },
};
