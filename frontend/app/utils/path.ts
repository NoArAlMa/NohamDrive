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

export const normalizePath = (path: string): string => {
  const segments = path.split("/").filter(Boolean);
  const stack: string[] = [];

  for (const segment of segments) {
    if (segment === ".") continue;
    if (segment === "..") {
      stack.pop();
    } else {
      stack.push(segment);
    }
  }

  return "/" + stack.join("/");
};

export function resolvePath(input: string, cwd: string): string {
  if (!input || input === ".") return cwd;

  // ~/ ou ~
  if (input === "~") return "/";
  if (input.startsWith("~/")) {
    input = "/" + input.slice(2);
  }

  const fullPath = input.startsWith("/") ? input : `${cwd}/${input}`;

  const parts = fullPath.split("/");
  const stack: string[] = [];

  for (const part of parts) {
    if (!part || part === ".") continue;
    if (part === "..") {
      stack.pop();
    } else {
      stack.push(part);
    }
  }

  return "/" + stack.join("/");
}
