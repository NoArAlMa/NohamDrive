import type { FileExistsResponse } from "~~/shared/types/file_request";
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
      const resolved_path = resolvePath(args[0], ctx.currentPath!);

      if (resolved_path === ctx.currentPath!) {
        return { type: "nope" };
      }

      try {
        const resolved = await $fetch<GenericAPIResponse<FileExistsResponse>>(
          "/storage/resolve",
          {
            params: { path: resolved_path },
          },
        );

        if (resolved.data!.type !== "directory") {
          return {
            type: "output",
            level: "error",
            content: "cd: not a directory",
          };
        }

        navigate(resolved_path);
        return { type: "nope" };
      } catch (e: any) {
        if (e.statusCode === 404) {
          return {
            type: "output",
            level: "error",
            content: "cd: no such file or directory",
          };
        }

        if (e.statusCode === 400) {
          return {
            type: "output",
            level: "error",
            content: "cd: invalid path",
          };
        }
      }
      return {
        type: "output",
        level: "error",
        content: "cd: unexpected error",
      };
    }

    return {
      type: "output",
      level: "error",
      content: "cd: unexpected error",
    };
  },
};
