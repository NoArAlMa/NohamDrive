export default defineAppConfig({
  ui: {
    icons: {
      loading: "material-symbols:progress-activity",
      check: "material-symbols:check-small-rounded",
    },
    storage: {
      type: "localStorage", // par défaut 'cookie', change pour localStorage
    },
  },
});
