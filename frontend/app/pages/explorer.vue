<script setup lang="ts">
const { t } = useI18n();

definePageMeta({
  layout: "default",
  middleware: "auth-middleware",
});

useHead({
  title: String(t("seo.explorerTitle")),
  meta: [
    {
      name: "NohamDrive | File Explorer",
      content: String(t("seo.explorerDescription")),
    },
  ],
});

useSeoMeta({
  description: String(t("seo.explorerDescription")),
  ogTitle: String(t("seo.explorerTitle")),
  ogDescription: String(t("seo.explorerDescription")),
  ogImage: "[og:image]",
  ogUrl: "[og:url]",
  twitterTitle: String(t("seo.explorerTitle")),
  twitterDescription: String(t("seo.explorerDescription")),
  twitterImage: "[twitter:image]",
  twitterCard: "summary",
});
</script>

<template>
  <section
    class="flex flex-1 overflow-hidden desktop:items-center desktop:justify-center desktop:px-4 desktop:py-6"
  >
    <div
      class="w-full h-full flex flex-col overflow-hidden desktop:max-w-7xl desktop:h-[80vh] desktop:rounded-md desktop:shadow-lg desktop:max-h-9/12"
    >
      <FileExplorerContainer class="flex-1 overflow-auto" />
    </div>
  </section>
</template>
