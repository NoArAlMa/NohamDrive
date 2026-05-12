<script lang="ts" setup>
const { t } = useI18n();

definePageMeta({
  layout: "default",
  middleware: "auth-middleware",
});

useHead({
  title: "Home - NohamDrive",
  meta: [
    {
      name: "NohamDrive | Home",
      content: "Panel of your account",
    },
  ],
});

useSeoMeta({
  description: "Panel of your account",
  ogTitle: "Home - NohamDrive",
  ogDescription: "Panel of your account",
  ogImage: "[og:image]",
  ogUrl: "[og:url]",
  twitterTitle: "Home - NohamDrive",
  twitterDescription: "Panel of your account",
  twitterImage: "[twitter:image]",
  twitterCard: "summary",
});
</script>

<template>
  <section class="h-full flex flex-col items-center justify-center">
    <h1 class="text-4xl text-neutral font-semibold mb-1">
      {{ t("home.wipTitle") }}
    </h1>
    <p class="text-muted text-md">{{ t("home.wipDesc") }}</p>
  </section>
</template>
