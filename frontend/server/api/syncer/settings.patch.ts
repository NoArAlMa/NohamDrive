import { runtimeState } from "../../state/runtime";
export default defineEventHandler(async (event) => {
  const runtime = runtimeState;

  const body = await readBody(event);

  if (!runtime?.host || !runtime?.port || !runtime?.token) {
    throw createError({
      statusCode: 500,
      message: String(runtime),
    });
  }

  const baseURL = `http://${runtime.host}:${runtime.port}`;
  const token = runtime.token;

  try {
    const data = await $fetch(`${baseURL}/settings/`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body,
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
