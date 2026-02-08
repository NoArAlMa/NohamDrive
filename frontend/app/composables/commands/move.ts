import type { MoveFilePayload } from "~~/shared/types/file_request";

export const moveCommand: TerminalCommand = {
  name: "mv",
  description: "Move a file or directory in a selected directory",
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

    if (args.length === 0 || args.length === 1) {
      return [
        {
          type: "output",
          level: "error",
          content: "mv : Usage - Needs at least 2 arguments",
        },
      ];
    }

    if (args.length === 2 && args[0] && args[1]) {
      const path = args[0];
      const destination_path = args[1];

      const correct_path = resolvePath(path, ctx?.currentPath!);
      const correct_destination_path = resolvePath(
        destination_path,
        ctx?.currentPath!,
      );

      const payload: MoveFilePayload = {
        source_path: correct_path,
        destination_folder: correct_destination_path,
      };

      try {
        await $fetch<GenericAPIResponse<string>>("/storage/move", {
          method: "POST",
          body: payload,
        });
        useFileTree().retryFetching();
        return [
          {
            type: "nope",
          },
        ];
      } catch (error: any) {
        const message =
          error.data?.statusMessage ||
          "Impossible de déplacer le fichier/dossier.";
        return [
          {
            type: "output",
            level: "error",
            content: `mv : ${message}`,
          },
        ];
      }
    }
    return [
      {
        type: "output",
        level: "error",
        content: `mv : Usage - Too many arguments`,
      },
    ];
  },
};
