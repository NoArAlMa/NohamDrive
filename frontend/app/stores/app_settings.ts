export const useSettingsStore = defineStore("settings", {
  state: () => ({
    settings: {
      token: "",
      drive_path: "",
      auto_start: true,
    },
  }),

  actions: {
    async fetch() {
      this.settings = await $fetch("/api/syncer/settings");
    },

    async update(key: string, value: any) {
      await $fetch(`/api/syncer/settings/${key}`, {
        method: "PATCH",
        body: {
          value,
        },
      });

      this.settings[key] = value;
    },
  },
});
