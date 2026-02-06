import type { CopyFilePayload } from "~~/shared/types/file_request";

export const copyCommand: TerminalCommand = {
  name: "copy",
  description: "Copy or duplicate a file or directory",
  run: async (args: string[], ctx) => {
    if (!ctx) {
      return [
        {
          type: "output",
          level: "error",
          content: "Internal error: missing context",
        },
      ];
    }

    if (args.length === 0) {
      return [
        {
          type: "output",
          level: "error",
          content: "copy : Usage - copy <source>",
        },
      ];
    }
    if (args[0]) {
      const sourcePath = resolvePath(args[0], ctx.currentPath!);
      const destination_folder = resolvePath(args[1] || "/", ctx.currentPath!);

      const payload: CopyFilePayload = {
        source_path: sourcePath,
        destination_folder: destination_folder,
      };

      try {
        await $fetch<GenericAPIResponse<CopyFilePayload>>("/storage/copy", {
          method: "POST",
          body: payload,
        });

        useFileTree().retryFetching();

        return [{ type: "nope" }];
      } catch (error: any) {
        const message =
          error.data?.statusMessage ||
          "Impossible de copier le fichier/dossier.";

        return [
          {
            type: "output",
            level: "error",
            content: `copy : ${message}`,
          },
        ];
      }
    }

    return [
      {
        type: "output",
        level: "error",
        content: `copy : Usage - Too many arguments`,
      },
    ];
  },
};
