import type { TerminalCommand } from "~~/shared/types/terminal_types";
import { commandRegistry } from "./index";

export const helpCommand: TerminalCommand = {
  name: "help",
  description: "Show help for commands",
  run: (args: string[]) => {
    if (args.length === 0) {
      const lines = Object.values(commandRegistry).map(
        (cmd) => `- ${cmd.name} : ${cmd.description}`,
      );

      return {
        type: "output",
        content: `Available commands:\n${lines.join("\n")}`,
      };
    }
    const target = args[0];
    if (!target) {
      return {
        type: "output",
        level: "error",
        content: `help : No help available for command: ${target}`,
      };
    }

    const command = commandRegistry[target as keyof typeof commandRegistry];

    return {
      type: "output",
      content: `${command.name} :\n${command.description}`,
    };
  },
};
