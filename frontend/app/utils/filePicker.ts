export function openFilePicker(multiple = true): Promise<File[]> {
  return new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = multiple;
    input.style.display = "none";

    input.onchange = () => {
      resolve(input.files ? Array.from(input.files) : []);
      input.remove();
    };

    document.body.appendChild(input);
    input.click();
  });
}
