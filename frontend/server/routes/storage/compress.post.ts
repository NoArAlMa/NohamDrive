import { GenericAPIResponse } from "~~/shared/types/API";
import { CompressFilePayload } from "~~/shared/types/file_request";

export default defineEventHandler(async (event) => {
  const payload = await readBody(event);
  const API_URL = useRuntimeConfig().public.apiBaseUrl;
  try {
    const data = await $fetch<GenericAPIResponse<CompressFilePayload>>(
      `${API_URL}/storage/compress`,
      {
        method: "POST",
        body: payload,
      }
    );
    return data;
  } catch (error: any) {
    if (error?.response?.status) {
      throw createError({
        statusCode: error.response.status,
        statusMessage:
          error.response._data?.message ??
          "Erreur lors de la récupération des fichiers",
      });
    }
    throw createError({
      statusCode: 500,
      statusMessage: "Serveur de stockage indisponible",
    });
  }
});
