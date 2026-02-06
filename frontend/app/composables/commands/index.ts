import { helpCommand } from "./help";
import { clearCommand } from "./clear";
import { uploadCommand } from "./upload";
import { listCommand } from "./list";
import { currentDirectoryCommand } from "./pwd";
import { changeDirectoryCommand } from "./cd";
import { makeDirectoryCommand } from "./mkdir";
import { removeCommand } from "./rm";
import { downloadCommand } from "./download";
import { moveCommand } from "./move";
import { renameCommand } from "./rename";
import { copyCommand } from "./copy";

export const commandRegistry = {
  help: helpCommand,
  clear: clearCommand,
  upload: uploadCommand,
  list: listCommand,
  pwd: currentDirectoryCommand,
  cd: changeDirectoryCommand,
  mkdir: makeDirectoryCommand,
  rm: removeCommand,
  download: downloadCommand,
  mv: moveCommand,
  rename: renameCommand,
  copy: copyCommand,
};
