export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",

  // Ignore le dossier electron
  ignore: ["electron"],

  modules: ["@nuxt/ui", "@pinia/nuxt", "@vueuse/nuxt", "nuxt-i18n-micro"],

  i18n: {
    locales: [
      { code: "fr", iso: "fr-FR", dir: "ltr", name: "Français" },
      { code: "en", iso: "en-US", dir: "ltr", name: "English" },
    ],
    defaultLocale: "fr",
    fallbackLocale: "fr",
    strategy: "prefix_except_default",
    translationDir: "locales",
    meta: true,
    autoDetectLanguage: true,
    localeCookie: "user-locale",
  },

  // Importation des fichiers css principaux

  css: ["~/assets/css/main.css"],

  app: {
    head: {
      title: "NohamDrive",
      htmlAttrs: {
        lang: "fr",
      },
      link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
    },
  },

  // Configuration du l'environnement
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL,
    },
  },

  icon: {
    serverBundle: {
      collections: ["material-symbols"],
    },
    customCollections: [
      {
        prefix: "explorer",
        dir: "./app/assets/icons/explorer/files",
      },
      {
        prefix: "desktop",
        dir: "./app/assets/icons/desktop",
      },
      {
        prefix: "terminal",
        dir: "./app/assets/icons/terminal",
      },
    ],
  },

  // Configuration de ColorMode
  colorMode: {
    preference: "dark",
    disableTransition: false,
  },

  build: {
    transpile: ["vue-files-preview"],
  },

  postcss: {
    plugins: {
      "@tailwindcss/postcss": {},
      autoprefixer: {},
      cssnano:
        process.env.NODE_ENV === "production"
          ? { preset: ["default", { discardComments: { removeAll: true } }] }
          : false,
    },
  },

  $production: {
    ssr: true,
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
