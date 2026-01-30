import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";

// function isPath(arg: string): boolean {
//   return (
//     arg.startsWith("/") || arg.includes("/") || arg === "." || arg === ".."
//   );
// }

export const listCommand: TerminalCommand = {
  name: "list",
  description: "List current files in dir",
  run: async (args: string[], ctx?: TerminalContext) => {
    if (!ctx) {
      return {
        type: "output",
        level: "error",
        content: "Internal error: missing context",
      };
    }

    if (args.length === 0) {
      const files = Object.values(ctx?.fileTree!).map(
        (file) => `${file.is_dir ? "[DIR] " : ""}${file.name}`,
      );

      return {
        type: "output",
        content: `${files.join("\n")}`,
      };
    }
    if (args.length === 1 && args[0]) {
      const path = args[0];

      try {
        const data = await $fetch<GenericAPIResponse<ApiFileTreeData>>(
          "/storage/tree",
          {
            method: "GET",
            params: { path: path },
          },
        );

        const Items = data.data?.items;

        if (!Items?.length) {
          return {
            type: "output",
            level: "default",
            content: "Folder is empty",
          };
        }
        const files = Object.values(data.data?.items!).map(
          (file) => `${file.is_dir ? "[DIR] " : ""}${file.name}`,
        );

        return {
          type: "output",
          content: `${files.join("\n")}`,
        };
      } catch (error: any) {
        const message =
          error.data?.statusMessage ||
          "Impossible de renommer le fichier/dossier.";
        return {
          type: "output",
          level: "error",
          content: message,
        };
      }
    }

    return {
      type: "output",
      level: "error",
      content: "Invalid arguments for list command.",
    };
  },
};
