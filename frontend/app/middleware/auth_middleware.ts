export default defineNuxtRouteMiddleware((to) => {
  const token = useCookie("auth_token");

  const invert = to.meta?.invertAuth;

  if (!invert && !token.value) {
    return navigateTo("/auth");
  }

  if (invert && token.value) {
    return navigateTo("/home");
  }
});
