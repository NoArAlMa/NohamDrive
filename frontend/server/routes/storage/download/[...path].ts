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

  const target = `${config.public.apiBaseUrl}/storage/download/${path}`;

  return proxyRequest(event, target);
});
