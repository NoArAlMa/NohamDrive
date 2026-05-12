import type { GenericAPIResponse } from "~~/shared/types/API";
import type { User, UserUpdatePayload } from "~~/shared/types/auth";

export default defineEventHandler(async (event) => {
  const payload = await readBody<UserUpdatePayload>(event);
  const token = getCookie(event, "auth_token");
  const API_URL = useRuntimeConfig().public.apiBaseUrl;

  try {
    const data = await $fetch<GenericAPIResponse<User>>(`${API_URL}/users/me`, {
      method: "PATCH",
      body: payload,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return data;
  } catch (error: any) {
    throw createError({
      statusCode: error?.response?.status ?? error?.statusCode ?? 500,
      data: error?.response?._data?.data ?? error?.data ?? {},
      message:
        error?.response?._data?.message ??
        error?.data?.message ??
        "Impossible de mettre à jour le profil",
    });
  }
});
