export default defineNuxtRouteMiddleware((to) => {
  const { isElectron } = useElectron();

  const invert = to.meta.invertElectronRedirect;

  console.log("isElectron:", isElectron.value);
  console.log("route:", to.fullPath);

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
