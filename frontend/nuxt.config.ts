export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },

  modules: ["@nuxt/ui", "@pinia/nuxt", "@vueuse/nuxt"],

  // Importation des fichiers css principaux

  css: ["~/assets/css/main.css"],

  // Configuration du l'environnement
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL,
    },
  },

  vite: {
    assetsInclude: ["**/*.svg"],
  },
});
