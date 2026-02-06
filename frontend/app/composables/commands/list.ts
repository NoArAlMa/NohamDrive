import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";

export const listCommand: TerminalCommand = {
  name: "list",
  description:
    "List files and directories in the current directory, or in a specified path: list [path]",
  run: async (args: string[], ctx?: TerminalContext) => {
    if (!ctx) {
      return {
        type: "output",
        level: "error",
        content: "Internal error: missing context",
      };
    }

    if (args.length === 0) {
      const items = ctx.fileTree ?? [];

      if (items.length === 0) {
        return {
          type: "output",
          level: "muted",
          content: "Folder is empty",
        };
      }

      const files = items.map(
        (file) => `${file.is_dir ? "[DIR] " : ""}${file.name}`,
      );

      return {
        type: "output",
        content: files.join("\n"),
      };
    }

    if (args.length === 1 && args[0]) {
      const path = args[0];
      const correct_path = resolvePath(path, ctx.currentPath!);

      try {
        const data = await $fetch<GenericAPIResponse<ApiFileTreeData>>(
          "/storage/tree",
          {
            method: "GET",
            params: { path: correct_path },
          },
        );

        const items = data.data?.items ?? [];

        if (items.length === 0) {
          return {
            type: "output",
            level: "muted",
            content: "Folder is empty",
          };
        }

        const files = items.map(
          (file) => `${file.is_dir ? "[DIR] " : ""}${file.name}`,
        );

        return {
          type: "output",
          content: files.join("\n"),
        };
      } catch (error: any) {
        const message =
          error.data?.statusMessage ||
          "Impossible de lister les fichiers/dossiers.";

        return {
          type: "output",
          level: "error",
          content: `list : ${message}`,
        };
      }
    }

    return {
      type: "output",
      level: "error",
      content: "list : Too many arguments for list command.",
    };
  },
};
