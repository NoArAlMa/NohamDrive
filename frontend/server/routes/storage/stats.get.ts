import { FileMetadata } from "../../../shared/types/file_metadata";
import { GenericAPIResponse } from "../../../shared/types/API";

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const object_path = query.object_path as string;

  const API_URL = useRuntimeConfig().public.apiBaseUrl;
  try {
    const data = await $fetch<GenericAPIResponse<FileMetadata>>(
      `${API_URL}/storage/stats`,
      {
        method: "GET",
        query: {
          object_path: object_path,
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
