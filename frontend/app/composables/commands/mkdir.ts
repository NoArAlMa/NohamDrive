import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";

export const makeDirectoryCommand: TerminalCommand = {
  name: "mkdir",
  description: "Create a directory: mkdir <name> or mkdir <path>",
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
        content:
          "mkdir : Missing directory name. Usage: mkdir <name> or mkdir <path + name>",
      };
    }

    if (args.length === 1) {
      const inputPath = args![0];
      const correctPath = resolvePath(inputPath!, ctx.currentPath!);

      const parts = correctPath.split("/").filter((p) => p !== "");
      const folderName = parts[parts.length - 1];
      const parentPath = parts.slice(0, -1).join("/") || "/";
      const { createFolder } = useFsActions();

      try {
        console.log(parentPath);
        console.log(folderName);
        const result = await createFolder(folderName!, parentPath);
        if (!result.success) {
          return {
            type: "output",
            level: "error",
            content: `mkdir: ${result.message || "Failed to create directory."}`,
          };
        }
        return {
          type: "nope",
        };
      } catch (error: any) {
        return {
          type: "output",
          level: "error",
          content: `mkdir: ${error.message || "An unexpected error occurred."}`,
        };
      }
    }

    return {
      type: "output",
      level: "error",
      content: "mkdir : Usage - Too many arguments",
    };
  },
};
