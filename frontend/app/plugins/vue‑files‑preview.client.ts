import { defineNuxtPlugin } from "#app";
import VueFilesPreview from "vue-files-preview";

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(VueFilesPreview);
});
