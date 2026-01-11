import { GenericAPIResponse } from "~~/shared/types/API";

interface MultipartFile {
  name?: string;
  filename?: string;
  data?: Uint8Array;
}

export default defineEventHandler(async (event) => {
  const API_URL = useRuntimeConfig().public.apiBaseUrl;

  try {
    const formData: MultipartFile[] =
      (await readMultipartFormData(event)) || [];

    // Récupérer le path ou fallback "/"
    const pathItem = formData.find((f) => f.name === "path" && f.data);
    const path = pathItem?.data?.toString() || "/";

    // Créer un FormData compatible fetch
    const uploadFormData = new FormData();

    for (const file of formData) {
      if (file.name && file.filename && file.data) {
        uploadFormData.append(
          file.name,
          new Blob([file.data]), // Blob obligatoire en Node
          file.filename
        );
      }
    }

    const res = await fetch(
      `${API_URL}/storage/upload?path=${encodeURIComponent(path)}`,
      {
        method: "POST",
        body: uploadFormData,
      }
    );

    return await res.json();
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      statusMessage: "Erreur proxy upload : " + error.message,
    });
  }
});
