export function formatFileSize(bytes?: number | null, decimals = 1): string {
  if (!bytes || bytes <= 0) return "--";

  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  const value = bytes / Math.pow(k, i);

  // Enlève les .0 inutiles
  const formatted =
    value % 1 === 0 ? value.toFixed(0) : value.toFixed(decimals);

  return `${formatted} ${sizes[i]}`;
}
