import { UserCreatePayload } from "./../../../shared/types/auth";
import { GenericAPIResponse } from "~~/shared/types/API";

export default defineEventHandler(async (event) => {
  const payload = await readBody<UserCreatePayload>(event);

  const API_URL = useRuntimeConfig().public.apiBaseUrl;

  try {
    const data = await $fetch<GenericAPIResponse<null>>(
      `${API_URL}/auth/register`,
      {
        method: "POST",
        body: payload,
      },
    );

    return data;
  } catch (error: any) {
    if (error?.response?.status) {
      throw createError({
        statusCode: error.response.status,
        data: error.response._data.data ?? {},
        message:
          error.response._data?.message ?? "Impossible de créer un compte",
      });
    }
    throw createError({
      statusCode: 500,
      statusMessage: "Serveur de stockage indisponible",
    });
  }
});
