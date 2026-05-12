<script lang="ts" setup>
const { t } = useI18n();

definePageMeta({
  layout: "default",
  middleware: "auth-middleware",
});

useHead(() => ({
  title: t("seo.terminalTitle"),
  meta: [
    {
      name: "NohamDrive | Echo",
      content: t("seo.terminalDescription"),
    },
  ],
}));

useSeoMeta(() => ({
  description: t("seo.terminalDescription"),
  ogTitle: t("seo.terminalTitle"),
  ogDescription: t("seo.terminalDescription"),
  ogImage: "[og:image]",
  ogUrl: "[og:url]",
  twitterTitle: t("seo.terminalTitle"),
  twitterDescription: t("seo.terminalDescription"),
  twitterImage: "[twitter:image]",
  twitterCard: "summary",
}));
</script>

<template>
  <Terminal />
</template>
