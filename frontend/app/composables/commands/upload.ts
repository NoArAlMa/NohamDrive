import type { TerminalCommand } from "~~/shared/types/terminal_types";

export const uploadCommand: TerminalCommand = {
  name: "upload",
  description: "Upload a file to OneDrive (mock)",
  run: (args: string[]) => {
    if (!args.length) {
      return {
        type: "output",
        level: "error",
        content: "Missing file name",
      };
    }

    const filename = args.join(" ");
    return {
      type: "output",
      content: `Uploading \"${filename}\"... (mock)`,
    };
  },
};
