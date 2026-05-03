export default function formatDate(value: string | number | Date) {
  if (!value) {
    return "--";
  }
  try {
    return new Date(value).toLocaleString("fr-FR", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  } catch {
    return value;
  }
}
 