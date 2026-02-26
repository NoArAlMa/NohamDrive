export default defineAppConfig({
  ui: {
    icons: {
      loading: "material-symbols:progress-activity",
      check: "material-symbols:check-small-rounded",
      menu: "material-symbols:menu-rounded",
      panelClose: "material-symbols:left-panel-close-outline-rounded",
      panelOpen: "material-symbols:left-panel-open-outline-rounded",
    },
    storage: {
      type: "localStorage", // par défaut 'cookie', change pour localStorage
    },
  },
});
