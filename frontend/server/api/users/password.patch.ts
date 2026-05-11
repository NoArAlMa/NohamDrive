import type { GenericAPIResponse } from "~~/shared/types/API";
import type { PasswordUpdatePayload } from "~~/shared/types/auth";

export default defineEventHandler(async (event) => {
  const payload = await readBody<PasswordUpdatePayload>(event);
  const token = getCookie(event, "auth_token");
  const API_URL = useRuntimeConfig().public.apiBaseUrl;

  try {
    const data = await $fetch<GenericAPIResponse<null>>(
      `${API_URL}/users/me/password`,
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
    throw createError({
      statusCode: error?.response?.status ?? error?.statusCode ?? 500,
      data: error?.response?._data?.data ?? error?.data ?? {},
      message:
        error?.response?._data?.message ??
        error?.data?.message ??
        "Impossible de mettre à jour le mot de passe",
    });
  }
});
