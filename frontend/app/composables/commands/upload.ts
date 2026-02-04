export const uploadCommand: TerminalCommand = {
  name: "upload",
  description: "Upload one or more files to the current directory",
  run: async (args: string[], ctx) => {
    if (!ctx) {
      return [
        {
          type: "output",
          level: "error",
          content: "Internal error: missing context",
        },
      ];
    }

    const files = await openFilePicker(true);

    if (files.length === 0) {
      return [
        {
          type: "output",
          level: "muted",
          content: "No file selected.",
        },
      ];
    }

    // Retourne un tableau de blocs de progression
    return files.map((file) => ({
      type: "progress" as const,
      id: crypto.randomUUID(),
      subject: file.name,
      loaded: 0,
      total: file.size,
      status: "pending" as const,
    }));
  },
};
