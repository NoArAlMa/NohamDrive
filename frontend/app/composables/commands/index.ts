import { helpCommand } from "./help";
import { clearCommand } from "./clear";
import { uploadCommand } from "./upload";
import { listCommand } from "./list";
import { currentDirectoryCommand } from "./pwd";
import { changeDirectoryCommand } from "./cd";

export const commandRegistry = {
  help: helpCommand,
  clear: clearCommand,
  upload: uploadCommand,
  list: listCommand,
  pwd: currentDirectoryCommand,
  cd: changeDirectoryCommand,
};
