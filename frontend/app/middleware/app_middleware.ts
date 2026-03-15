export default defineNuxtRouteMiddleware(() => {
  const { isElectron } = useElectron();
  if (isElectron.value) {
    return navigateTo("/home");
  }
});
