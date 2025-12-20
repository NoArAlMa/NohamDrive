import { ApiFileTreeResponse } from "~~/shared/types/file_tree";

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const path = (query.path as string) || "/";
  const API_URL = useRuntimeConfig().public.apiBaseUrl;
  try {
    const data = await $fetch<ApiFileTreeResponse[]>(
      `${API_URL}/storage/tree?path=${encodeURIComponent(path)}`,
      {
        method: "GET",
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
