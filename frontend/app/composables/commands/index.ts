import { helpCommand } from "./help";
import { clearCommand } from "./clear";
import { uploadCommand } from "./upload";

export const commandRegistry = {
  help: helpCommand,
  clear: clearCommand,
  upload: uploadCommand,
};
