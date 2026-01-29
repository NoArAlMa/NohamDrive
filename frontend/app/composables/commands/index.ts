import { helpCommand } from "./help";
import { clearCommand } from "./clear";
import { uploadCommand } from "./upload";
import { listCommand } from "./list";

export const commandRegistry = {
  help: helpCommand,
  clear: clearCommand,
  upload: uploadCommand,
  list: listCommand,
};
