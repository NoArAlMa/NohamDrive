export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",

  // Ignore le dossier electron
  ignore: ["electron"],

  modules: ["@nuxt/ui", "@pinia/nuxt", "@vueuse/nuxt", "@nuxt/hints"],

  // Importation des fichiers css principaux

  css: ["~/assets/css/main.css"],

  // Configuration du l'environnement
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL,
    },
  },

  // Configuration de ColorMode
  colorMode: {
    preference: "dark",
    disableTransition: false,
  },

  build: {
    transpile: ["vue-files-preview"],
  },

  $production: {
    ssr: false,
    nitro: {
      compressPublicAssets: true,
      minify: true,
    },
    devtools: { enabled: false },
  },

  $development: {
    ssr: true,
    devtools: { enabled: true },
  },

  vite: {
    css: {
      devSourcemap: true,
    },
    build: {
      sourcemap: process.env.NODE_ENV === "development",
    },
  },
});
