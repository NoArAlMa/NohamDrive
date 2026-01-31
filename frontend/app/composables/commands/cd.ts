import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";

export const changeDirectoryCommand: TerminalCommand = {
  name: "cd",
  description: "Change the current directory",
  run: async (args: string[], ctx?: TerminalContext) => {
    if (!ctx) {
      return {
        type: "output",
        level: "error",
        content: "Internal error: missing context",
      };
    }

    if (args.length === 0) {
      return {
        type: "output",
        level: "error",
        content: "Usage : command cd needs at least 1 argument",
      };
    }

    if (args.length > 1) {
      return {
        type: "output",
        level: "error",
        content: "cd: too many arguments",
      };
    }

    if (args.length === 1 && args[0]) {
      const { navigate } = useFSStore();
      const path = args[0];
      navigate(path);
      return null;
    }

    return {
      type: "output",
      level: "error",
      content: "Invalid arguments for cd command.",
    };
  },
};
