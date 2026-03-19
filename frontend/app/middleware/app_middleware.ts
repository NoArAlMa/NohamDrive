export default defineNuxtRouteMiddleware((to) => {
  const { isElectron } = useElectron();

  const invert = to.meta.invertElectronRedirect;

  if (invert) {
    if (!isElectron.value) {
      return navigateTo("/home");
    }
  } else {
    if (isElectron.value) {
      return navigateTo("/home");
    }
  }
});
