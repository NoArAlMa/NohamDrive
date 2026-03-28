import { GenericAPIResponse } from "~~/shared/types/API";
import { RenameFilePayload } from "~~/shared/types/file_request";

export default defineEventHandler(async (event) => {
  const payload = await readBody(event);

  const API_URL = useRuntimeConfig().public.apiBaseUrl;
  const token = getCookie(event, "auth_token");
  try {
    const data = (await $fetch)<GenericAPIResponse<RenameFilePayload>>(
      `${API_URL}/storage/rename`,
      {
        method: "PATCH",
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
