export const fileIconMap: Record<string, string> = {
  pdf: "pdf",
  doc: "doc",
  docx: "doc",
  xls: "xls",
  xlsx: "xls",
  png: "image",
  jpg: "image",
  jpeg: "image",
  mp4: "video",
  mp3: "audio",
  zip: "zip",
  rar: "zip",
};

export const getFileIcon = (filename: string) => {
  const ext = filename.split(".").pop()?.toLowerCase();
  return fileIconMap[ext ?? ""] ?? "unknown";
};
