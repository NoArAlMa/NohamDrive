import type { ApiFileItem } from "./file_tree";

export type TerminalBlock =
  | {
      type: "command";
      content: string;
      cwd: string;
    }
  | {
      type: "output";
      content: string;
      level?: "default" | "info" | "success" | "warning" | "error" | "muted";
    };

export type CommandResult =
  | {
      type: "output";
      content: string | any;
      level?: "default" | "info" | "success" | "warning" | "error" | "muted";
    }
  | { type: "clear" }
  | { type: "nope" };

export interface TerminalContext {
  fileTree?: ApiFileItem[];
  currentPath?: string;
}

export interface TerminalCommand {
  name: string;
  aliases?: string[];
  description: string;
  run: (
    args: string[],
    context?: TerminalContext,
  ) => CommandResult | Promise<CommandResult>;
}
