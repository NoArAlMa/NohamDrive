export const fileIconMap: Record<string, string> = {
  // Documents
  pdf: "vscode-icons:file-type-pdf2",
  doc: "vscode-icons:file-type-word",
  docx: "vscode-icons:file-type-word",
  xls: "i-vscode-icons:file-type-excel",
  xlsx: "i-vscode-icons:file-type-excel2",
  ppt: "vscode-icons:file-type-powerpoint",
  pptx: "vscode-icons:file-type-powerpoint",
  txt: "vscode-icons:file-type-text",
  csv: "material-symbols:csv-outline-rounded",
  md: "vscode-icons:file-type-markdown",

  // Images
  png: "vscode-icons:file-type-image",
  jpg: "vscode-icons:file-type-image",
  jpeg: "vscode-icons:file-type-image",
  webp: "vscode-icons:file-type-image",
  svg: "vscode-icons:file-type-image",

  // Archives
  rar: "vscode-icons:file-type-zip",
  zip: "vscode-icons:file-type-zip",

  // Médias
  mp4: "vscode-icons:file-type-video",
  mp3: "vscode-icons:file-type-audio",

  // Code
  js: "vscode-icons:file-type-js-official",
  py: "vscode-icons:file-type-python",
  css: "vscode-icons:file-type-css2",

  // Par défaut
  unknown: "heroicons:document",
};

// Fonction qui retourne le nom de l'icone en fonction de son extension

export const getFileIcon = (filename: string) => {
  const ext = filename.split(".").pop()?.toLowerCase();
  return fileIconMap[ext ?? ""] ?? "heroicons:document";
};
