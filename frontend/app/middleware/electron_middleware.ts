export default defineNuxtRouteMiddleware((to) => {
  const { isElectron } = useElectron();

  const isElectronRoute = to.query.electron === "true";

  if (isElectron.value || isElectronRoute) {
    return;
  }
  return navigateTo("/");
});
