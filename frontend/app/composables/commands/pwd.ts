import type { TerminalCommand } from "~~/shared/types/terminal_types";

export const currentDirectoryCommand: TerminalCommand = {
  name: "pwd",
  description: "Display the absolute path of the current working directory",
  run: (args: string[], ctx) => {
    if (args.length) {
      return {
        type: "output",
        level: "error",
        content: "Usage : command pwd doesn't take arguments",
      };
    }

    if (!ctx?.currentPath) {
      return {
        type: "output",
        level: "error",
        content: "Internal error: missing context",
      };
    }

    return {
      type: "output",
      level: "info",
      content: ctx?.currentPath,
    };
  },
};
