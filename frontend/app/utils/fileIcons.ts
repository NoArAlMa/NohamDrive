export const fileIconMap: Record<string, string> = {
  // Documents
  pdf: "file-pdf",
  doc: "file-word",
  docx: "file-word",
  xls: "i-vscode-icons:file-type-excel",
  xlsx: "i-vscode-icons:file-type-excel2",
  ppt: "file-powerpoint",
  pptx: "file-powerpoint",
  txt: "file-text",
  csv: "i-vscode-icons:file-type-csv",
  md: "file-markdown",

  // Images
  png: "file-image",
  jpg: "file-image",
  jpeg: "file-image",
  webp: "file-image",
  svg: "file-image",

  // Archives
  zip: "file-zip",
  rar: "file-zip",

  // Médias
  mp4: "file-video",
  mp3: "file-audio",

  // Code
  js: "file-js",
  py: "file-python",
  css: "file-css",

  // Par défaut
  unknown: "file-unknown",
};

export const getFileIcon = (filename: string) => {
  const ext = filename.split(".").pop()?.toLowerCase();
  return fileIconMap[ext ?? ""] ?? "file-unknown";
};
