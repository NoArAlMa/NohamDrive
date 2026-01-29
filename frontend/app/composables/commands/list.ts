import type {
  TerminalCommand,
  TerminalContext,
} from "~~/shared/types/terminal_types";

export const listCommand: TerminalCommand = {
  name: "list",
  description: "List current files in dir",
  run: (args: string[], ctx?: TerminalContext) => {
    const files = Object.values(ctx?.fileTree!).map((file) => `- ${file.name}`);
    console.info(files);
    return {
      type: "output",
      content: `${files.join("\n")}`,
    };
  },
};
