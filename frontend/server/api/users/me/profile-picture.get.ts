import { defineEventHandler, proxyRequest } from "h3";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  const token = getCookie(event, "auth_token");

  const target = `${config.public.apiBaseUrl}/users/me/profile-picture`;

  return proxyRequest(event, target, {
    headers: {
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });
});

