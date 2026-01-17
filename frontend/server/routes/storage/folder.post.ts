import { GenericAPIResponse } from "~~/shared/types/API";
import { CreateFolderPayload } from "~~/shared/types/file_request";

export default defineEventHandler(async (event) => {

  const payload = await readBody<CreateFolderPayload>(event);

  const API_URL = useRuntimeConfig().public.apiBaseUrl;

  try {
    const data = await $fetch<GenericAPIResponse<string>>(
      `${API_URL}/storage/folder`,
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
          error.response._data?.message ?? "Impossible de créer le dossier",
      });
    }
    throw createError({
      statusCode: 500,
      statusMessage: "Serveur de stockage indisponible",
    });
  }
});
