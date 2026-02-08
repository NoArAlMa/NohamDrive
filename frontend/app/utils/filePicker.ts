export function openFilePicker(multiple = true): Promise<File[]> {
  return new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = multiple;
    input.style.display = "none";

    let resolved = false;

    const cleanup = () => {
      window.removeEventListener("focus", onFocus);
      input.remove();
    };

    const onFocus = () => {
      // Si aucun onchange n’a eu lieu annul via la croix
      setTimeout(() => {
        if (!resolved) {
          resolved = true;
          cleanup();
          resolve([]);
        }
      }, 0);
    };

    input.onchange = () => {
      if (resolved) return;
      resolved = true;
      cleanup();
      resolve(input.files ? Array.from(input.files) : []);
    };

    window.addEventListener("focus", onFocus, { once: true });

    document.body.appendChild(input);
    input.click();
  });
}
