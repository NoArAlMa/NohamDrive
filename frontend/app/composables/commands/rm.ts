import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";

export const removeCommand: TerminalCommand = {
  name: "rm",
  description: "Delete a file or a directory",
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
        content: `rm : Needs at least 1 argument <path>`,
      };
    }
    if (args.length === 1 && args[0]) {
      const path = args[0];

      const correct_path = resolvePath(path, ctx?.currentPath!);

      if (correct_path == ctx.currentPath) {
        const files = Object.values(ctx?.fileTree!).map(
          (file) => `${file.is_dir ? "[DIR] " : ""}${file.name}`,
        );

        return {
          type: "output",
          content: `${files.join("\n")}`,
        };
      }
      try {
        const { retryFetching } = useFileTree();
        const data = await $fetch<GenericAPIResponse<null>>("/storage/object", {
          method: "DELETE",
          query: { folder_path: correct_path },
        });
        await retryFetching();
        return {
          type: "nope",
        };
      } catch (e: any) {
        const message =
          e.data?.statusMessage || "Fail to delete file/directory";
        return {
          type: "output",
          level: "error",
          content: `rm : ${message}`,
        };
      }
    }

    return {
      type: "output",
      level: "error",
      content: "rm : Invalid arguments for rm command.",
    };
  },
};
