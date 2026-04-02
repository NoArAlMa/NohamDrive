import { GenericAPIResponse } from "~~/shared/types/API";
import { UserLoginPayload } from "~~/shared/types/auth";

export default defineEventHandler(async (event) => {
  const payload = await readBody<UserLoginPayload>(event);

  const API_URL = useRuntimeConfig().public.apiBaseUrl;

  try {
    const data = await $fetch<GenericAPIResponse<null>>(
      `${API_URL}/auth/login`,
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
        message: error.response._data?.message ?? "Impossible de se connecter",
      });
    }
    throw createError({
      statusCode: 500,
      statusMessage: "Serveur de stockage indisponible",
    });
  }
});
