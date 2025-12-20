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
  } catch (error) {
    console.error("Erreur lors du fetch de l'arborescence :", error);
    throw createError({
      statusCode: 500,
      statusMessage: "Impossible de récupérer l'arborescence",
    });
  }
});
