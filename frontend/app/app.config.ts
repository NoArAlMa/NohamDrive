export default defineAppConfig({
  ui: {
    icons: {
      loading: "material-symbols:progress-activity",
      // ...
    },
    storage: {
      type: "localStorage", // par défaut 'cookie', change pour localStorage
    },
  },
});
