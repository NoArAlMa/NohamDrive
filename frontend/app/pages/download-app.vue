<script lang="ts" setup>
const { t } = useI18n();

useHead({
  title: String(t("download.headTitle")),
  meta: [
    {
      name: "Download Page",
      content: String(t("download.ctaDesc")),
    },
  ],
});

useSeoMeta({
  description:  String(t("download.ctaDesc")),
  ogTitle:  String(t("download.headTitle")),
  ogDescription:  String(t("download.ctaDesc")),
  ogImage: "[og:image]",
  ogUrl: "[og:url]",
  twitterTitle:  String(t("download.headTitle")),
  twitterDescription:  String(t("download.ctaDesc")),
  twitterImage: "[twitter:image]",
  twitterCard: "summary",
});

import type { ButtonProps } from "@nuxt/ui";

const links = computed<ButtonProps[]>(() => [
  {
    label: t("download.windows") as string,
    color: "primary",
    variant: "outline",
    leadingIcon: "desktop:windows-icon",
    to: "https://github.com/NoArAlMa/NohamDrive/releases/latest/download/NohamDrive-Setup.exe",
    target: "_blank",
  },
  {
    label: t("download.mac") as string,
    color: "neutral",
    variant: "outline",
    leadingIcon: "desktop:apple-icon",
    to: "https://www.apple.com/fr/",
    target: "_blank",
  },
]);
</script>

<template>
  <UPageCTA
    class="w-full h-full flex items-center justify-center"
    :title="String(t('download.ctaTitle'))"
    :description="String(t('download.ctaDesc'))"
    variant="subtle"
    :links="links"
    orientation="horizontal"
  >
    <img
      src="https://i.pinimg.com/736x/36/45/d5/3645d52b294d4b1d585c972eb4c05558.jpg"
      width="320"
      height="364"
      alt="Illustration"
      class="w-full rounded-lg"
    />
  </UPageCTA>
</template>
