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
    throw createError({
      statusCode: error.statusCode ?? 500,
      statusMessage:
        error.data?.message ??
        error.statusMessage ??
        "Erreur lors de la récupération des stats",
    });
  }
});
