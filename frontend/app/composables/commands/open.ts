import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";
import { joinPath, resolvePath } from "~/utils/path";

export const openCommand: TerminalCommand = {
  name: "open",
  description: "Open a specific file or directory",
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
        content: "open : Usage - Needs at least 1 argument <path>",
      };
    }

    if (args.length === 1 && args[0]) {
      const { open } = useFsActions();
      const targetName = args[0];
      const correct_path = resolvePath(targetName, ctx.currentPath!);

      const targetItem = ctx.fileTree?.find((item) => {
        const itemPath = joinPath(ctx.currentPath!, item.name);
        return itemPath === correct_path;
      });

      if (!targetItem) {
        return {
          type: "output",
          level: "error",
          content: `open : No such file or directory: ${targetName}`,
        };
      }

      try {
        await open(targetItem);
        return {
          type: "nope",
        };
      } catch (error: any) {
        const message =
          error.data?.statusMessage || "Impossible d'ouvrir le fichier.";
        return {
          type: "output",
          level: "error",
          content: `open : ${message}`,
        };
      }
    }

    return {
      type: "output",
      level: "error",
      content: "open : Too many arguments for open command.",
    };
  },
};
