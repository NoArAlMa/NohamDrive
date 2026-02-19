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
  const normalizedPath = Array.isArray(path) ? path.join("/") : path;

  const target = `${config.public.apiBaseUrl}/storage/preview/${normalizedPath}`;

  return proxyRequest(event, target);
});
