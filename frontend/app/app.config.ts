export default defineAppConfig({
  ui: {
    icons: {
      loading: "material-symbols:progress-activity",
      check: "material-symbols:check-small-rounded",
      menu: "material-symbols:menu-rounded",
      panelClose: "material-symbols:left-panel-close-outline-rounded",
      panelOpen: "material-symbols:left-panel-open-outline-rounded",
      search: "material-symbols:search-rounded",
      chevronDown: "material-symbols:keyboard-arrow-down-rounded",
    },
    storage: {
      type: "localStorage", // pas sur que ça marche mais ok
    },
  },
});
