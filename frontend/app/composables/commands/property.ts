import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";
import { joinPath, resolvePath } from "~/utils/path";
import formatDate from "~/utils/date";

export const propertyCommand: TerminalCommand = {
  name: "info",
  description: "Display properties of a file or directory",
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
        content: "property : Usage - Needs at least 1 argument <path>",
      };
    }

    if (args.length === 1 && args[0]) {
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
          content: `property : No such file or directory: ${targetName}`,
        };
      }

      try {
        // Effectue le fetch directement
        const req = await $fetch<GenericAPIResponse<FileMetadata>>(
          "/storage/stats",
          {
            method: "GET",
            query: {
              object_path: correct_path,
            },
          },
        );

        const metadata = req.data!;

        // Génère la sortie en fonction du type de fichier
        let output = `
Name: ${metadata.name}
Path: ${metadata.path}
Last modified: ${formatDate(metadata.last_modified!)}
Type: ${metadata.content_type}
Size: ${metadata.size_bytes ? formatFileSize(metadata.size_bytes, 1) : "N/A"}
        `;

        // Ajoute les propriétés spécifiques selon le type de fichier
        switch (metadata.content_type) {
          case "folder":
            output += `
Number of files: ${metadata.file_count ?? "N/A"}
            `;
            break;
          case "image":
            output += `
Width: ${metadata.width ?? "N/A"}px
Height: ${metadata.height ?? "N/A"}px
Format: ${metadata.format ?? "N/A"}
            `;
            break;
          case "video":
            output += `
Width: ${metadata.width ?? "N/A"}px
Height: ${metadata.height ?? "N/A"}px
Duration: ${metadata.duration ? formatDuration(metadata.duration) : "N/A"}
Codec: ${metadata.codec ?? "N/A"}
Framerate: ${metadata.fps ?? "N/A"} FPS
            `;
            break;
          default:
            // Pour les fichiers génériques (non image/vidéo/dossier)
            break;
        }

        return {
          type: "output",
          level: "info",
          content: output.trim(),
        };
      } catch (error: any) {
        const message =
          error.data?.statusMessage ||
          "Impossible de récupérer les propriétés.";
        return {
          type: "output",
          level: "error",
          content: `property : ${message}`,
        };
      }
    }

    return {
      type: "output",
      level: "error",
      content: "property : Too many arguments for property command.",
    };
  },
};
