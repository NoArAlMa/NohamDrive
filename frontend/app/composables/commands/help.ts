import type { TerminalCommand } from "~~/shared/types/terminal_types";

export const helpCommand: TerminalCommand = {
  name: "help",
  description: "List available commands",
  run: () => {
    return {
      type: "output",
      content: `Available commands:
- help
- upload
- clear`,
    };
  },
};
