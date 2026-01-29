import type { ApiFileItem } from "./file_tree";

export type Block =
  | { type: "command"; content: string }
  | { type: "output"; content: string }
  | { type: "error"; content: string };

export type CommandResult =
  | { type: "output"; content: string }
  | { type: "error"; content: string }
  | { type: "clear" };

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
