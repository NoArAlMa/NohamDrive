import type { RenameFilePayload } from "~~/shared/types/file_request";

function applyExtensionIfMissing(oldName: string, newName: string): string {
  const oldParts = oldName.split("/");
  const oldBase = oldParts.pop()!;

  const newParts = newName.split("/");
  const newBase = newParts.pop()!;

  // Dossier → rien à faire
  if (!oldBase.includes(".")) {
    return newName;
  }

  // Extension source (gère .tar.gz)
  const oldExt = oldBase.slice(oldBase.indexOf("."));

  // Le nouveau nom a déjà une extension
  if (newBase.includes(".")) {
    return newName;
  }

  return [...newParts, newBase + oldExt].join("/");
}

export const renameCommand: TerminalCommand = {
  name: "rename",
  description: "Rename a file or directory",
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
          content: "rename : Usage - Needs at least 2 arguments",
        },
      ];
    }

    if (args.length === 2 && args[0] && args[1]) {
      const path = args[0];
      const new_name = args[1];

      const correct_path = resolvePath(path, ctx?.currentPath!);
      const raw_new_path = resolvePath(new_name, ctx.currentPath!);

      const final_new_path = applyExtensionIfMissing(
        correct_path,
        raw_new_path,
      );

      const payload: RenameFilePayload = {
        path: correct_path,
        new_name: final_new_path,
      };

      try {
        await $fetch<GenericAPIResponse<string>>("/storage/rename", {
          method: "PATCH",
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
            content: `rename : ${message}`,
          },
        ];
      }
    }
    return [
      {
        type: "output",
        level: "error",
        content: `rename : Usage - Too many arguments`,
      },
    ];
  },
};
