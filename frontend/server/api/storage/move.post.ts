import { GenericAPIResponse } from "~~/shared/types/API";
import { MoveFilePayload } from "~~/shared/types/file_request";

export default defineEventHandler(async (event) => {
  const payload = await readBody<MoveFilePayload>(event);

  const API_URL = useRuntimeConfig().public.apiBaseUrl;
  const token = getCookie(event, "auth_token");

  try {
    const data = await $fetch<GenericAPIResponse<string>>(
      `${API_URL}/storage/move`,
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
          "Impossible de déplacer le fichier/dossier",
      });
    }
    throw createError({
      statusCode: 500,
      statusMessage: "Serveur de stockage indisponible",
    });
  }
});
