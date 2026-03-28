export function openFilePicker(multiple = true): Promise<File[]> {
  return new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = multiple;
    input.style.display = "none";

    let resolved = false;

    const cleanup = () => {
      window.removeEventListener("focus", onFocus);
      document.body.removeChild(input);
    };

    const onFocus = () => {
      setTimeout(() => {
        if (!resolved) {
          resolved = true;
          cleanup();

          resolve([]);
        }
      }, 500);
    };

    // Gère la sélection de fichiers
    const onChange = () => {
      if (resolved) return;
      resolved = true;
      cleanup();
      const files = input.files ? Array.from(input.files) : [];

      resolve(files);
    };

    input.addEventListener("change", onChange, { once: true });
    window.addEventListener("focus", onFocus, { once: true });
    document.body.appendChild(input);
    input.click();

    setTimeout(() => {
      if (!resolved) {
        resolved = true;
        cleanup();
        resolve([]);
      }
    }, 10000);
  });
}
