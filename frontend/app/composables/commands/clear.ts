import type { TerminalCommand } from "~~/shared/types/terminal_types";

export const clearCommand: TerminalCommand = {
  name: "clear",
  description: "Clear the terminal",
  run: () => {
    return {
      type: "clear",
    };
  },
};
