import { GenericAPIResponse } from "../../../shared/types/API";

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const path = query.folder_path as string;

  const API_URL = useRuntimeConfig().public.apiBaseUrl;
  try {
    const data = await $fetch<GenericAPIResponse<null>>(
      `${API_URL}/storage/object`,
      {
        method: "DELETE",
        query: {
          folder_path: path,
        },
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
