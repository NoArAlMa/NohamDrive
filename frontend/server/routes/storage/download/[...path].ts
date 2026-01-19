import { defineEventHandler, proxyRequest } from "h3";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  const path = event.context.params?.path;
  if (!path) {
    throw createError({
      statusCode: 400,
      statusMessage: "Chemin manquant",
    });
  }
  // path peut être string OU string[]
  const normalizedPath = Array.isArray(path) ? path.join("/") : path;

  const target = `${config.public.apiBaseUrl}/storage/download/${normalizedPath}`;

  return proxyRequest(event, target);
});
