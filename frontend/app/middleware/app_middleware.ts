export default defineNuxtRouteMiddleware(() => {
  const { isElectron } = useElectron();
  if (isElectron) {
    return navigateTo("/home");
  }
});
