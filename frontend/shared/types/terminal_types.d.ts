import type { ApiFileItem } from "./file_tree";

export interface OutputBlock {
  type: "output";
  content: string;
  level?: "default" | "info" | "success" | "warning" | "error" | "muted";
}

export interface CommandBlock {
  type: "command";
  content: string;
  cwd: string;
}

export interface ProgressBlock {
  type: "progress";
  id: string;
  subject: string;
  loaded: number;
  total: number;
  status: "pending" | "uploading" | "success" | "error";
}

export type TerminalBlock =
  | CommandBlock
  | OutputBlock
  | ProgressBlock
  | { type: "clear" }
  | { type: "nope" };

export type CommandResult =
  | OutputBlock
  | { type: "clear" }
  | { type: "nope" }
  | ProgressBlock;

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
  ) =>
    | CommandResult
    | Promise<CommandResult>
    | CommandResult[]
    | Promise<CommandResult[]>;
}
