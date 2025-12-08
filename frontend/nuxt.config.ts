export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: {
    enabled: process.env.NODE_ENV === "development",
  },

  modules: ["@nuxt/ui", "@pinia/nuxt", "@vueuse/nuxt"],

  // Importation des fichiers css principaux

  css: ["~/assets/css/main.css"],

  // Configuration du l'environnement
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL,
    },
  },

  routeRules: {
    "/routes/**": {
      proxy: {
        to: `${process.env.NUXT_PUBLIC_API_BASE_URL}/**`,
      },
    },
  },

  $production: {
    ssr: true,

    nitro: {
      compressPublicAssets: true,
      minify: true,
    },
  },

  $development: {
    ssr: true,
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