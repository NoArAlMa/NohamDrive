import { runtimeState } from "../../state/runtime";
export default defineEventHandler(async (event) => {
  const runtime = runtimeState;

  const query = getQuery(event);
  const value = (query.value as string) || "/";

  if (!runtime?.host || !runtime?.port || !runtime?.token) {
    throw createError({
      statusCode: 500,
      message: String(runtime),
    });
  }

  const baseURL = `http://${runtime.host}:${runtime.port}`;
  const token = runtime.token;

  try {
    const data = await $fetch(`${baseURL}/settings/${value}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return data;
  } catch (error: any) {
    if (error?.response?.status) {
      throw createError({
        statusCode: error.response.status,
        message:
          error.response._data?.message ?? "Erreur lors du contact de l'API",
      });
    }

    throw createError({
      statusCode: 500,
      message: "Système de synchronisation indisponible",
    });
  }
});
