export type Block =
  | { type: "command"; content: string }
  | { type: "output"; content: string }
  | { type: "error"; content: string };

export type CommandResult =
  | { type: "output"; content: string }
  | { type: "error"; content: string }
  | { type: "clear" };

export interface TerminalCommand {
  name: string;
  aliases?: string[];
  description: string;
  run: (args: string[]) => CommandResult | Promise<CommandResult>;
}
