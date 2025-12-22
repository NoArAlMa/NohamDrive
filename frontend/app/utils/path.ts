export function joinPath(...parts: string[]) {
  return (
    parts.filter(Boolean).join("/").replace(/\/+/g, "/").replace(/\/$/, "") ||
    "/"
  );
}

export function splitFilename(name: string) {
  const lastDot = name.lastIndexOf(".");

  // Dossier ou fichier sans extension
  if (lastDot <= 0) {
    return {
      base: name,
      ext: "",
      hasExtension: false,
    };
  }

  return {
    base: name.slice(0, lastDot),
    ext: name.slice(lastDot),
    hasExtension: true,
  };
}
