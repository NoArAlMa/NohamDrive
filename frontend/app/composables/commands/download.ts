import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";

export const downloadCommand: TerminalCommand = {
  name: "download",
  description: "Download a file or a directory",
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
        content: `download : Needs at least 1 argument <path>`,
      };
    }
    if (args.length === 1 && args[0]) {
      const path = args[0];

      const correct_path = resolvePath(path, ctx?.currentPath!);

      try {
        const response = await fetch(
          `/storage/download/${encodeURIComponent(correct_path)}`,
        );

        if (!response.ok) {
          const text = await response.text();
          return {
            type: "output",
            level: "error",
            content: `download: ${text || "failed to download"}`,
          };
        }

        const blob = await response.blob();

        const contentDisposition =
          response.headers.get("Content-Disposition") ?? "";

        const filename =
          contentDisposition.match(/filename\*?="?([^"]+)"?/i)?.[1] ??
          correct_path.split("/").pop() ??
          "download";

        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = decodeURIComponent(filename);
        a.rel = "noopener";
        document.body.appendChild(a);
        a.click();
        a.remove();

        URL.revokeObjectURL(url);

        return {
          type: "output",
          level: "success",
          content: "Fichier téléchargé",
        };
      } catch (e: any) {
        const message =
          e.data?.statusMessage || "Fail to download file/directory";
        return {
          type: "output",
          level: "error",
          content: `download : ${message}`,
        };
      }
    }

    return {
      type: "output",
      level: "error",
      content: "download : Invalid arguments for rm command.",
    };
  },
};
