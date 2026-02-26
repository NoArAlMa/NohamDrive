export const fileIconMap: Record<string, string> = {
  // Documents
  pdf: "explorer:pdf-icon",
  doc: "explorer:word-icon",
  docx: "explorer:word-icon",
  xls: "explorer:excel-icon",
  xlsx: "explorer:excel-icon",
  ppt: "explorer:powerpoint-icon",
  pptx: "explorer:powerpoint-icon",
  txt: "explorer:text-icon",
  csv: "material-symbols:csv-outline-rounded",
  md: "explorer:md-icon",

  // Images
  png: "explorer:image-icon",
  jpg: "explorer:image-icon",
  jpeg: "explorer:image-icon",
  webp: "explorer:image-icon",
  svg: "explorer:image-icon",

  // Archives
  rar: "explorer:zip-icon",
  zip: "explorer:zip-icon",

  // Médias
  mp4: "explorer:video-icon",
  mp3: "explorer:sound-icon",

  // Code
  js: "explorer:js-icon",
  py: "explorer:py-icon",
  css: "explorer:css-icon",

  // Par défaut
  unknown: "explorer:folder-icon",
};

// Fonction qui retourne le nom de l'icone en fonction de son extension

export const getFileIcon = (filename: string) => {
  const ext = filename.split(".").pop()?.toLowerCase();
  return fileIconMap[ext ?? "unknown"];
};
