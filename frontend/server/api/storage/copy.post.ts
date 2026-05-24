import type { GenericAPIResponse } from "~~/shared/types/API";
import type { CopyFilePayload } from "~~/shared/types/file_request";

export default defineEventHandler(async (event) => {
  const payload = await readBody(event);
  const API_URL = useRuntimeConfig().public.apiBaseUrl;
  const token = getCookie(event, "auth_token");
  try {
    const data = await $fetch<GenericAPIResponse<CopyFilePayload>>(
      `${API_URL}/storage/copy`,
      {
        method: "POST",
        body: payload,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
    return data;
  } catch (error: any) {
    if (error?.response?.status) {
      throw createError({
        statusCode: error.response.status,
        message:
          error.response._data?.message ??
          "Erreur lors de la récupération des fichiers",
      });
    }
    throw createError({
      statusCode: 500,
      message: "Serveur de stockage indisponible",
    });
  }
});
