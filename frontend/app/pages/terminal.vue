<script lang="ts" setup>
definePageMeta({
  layout: "default",
  middleware: "auth-middleware",
});

useHead({
  title: "Echo - NohamDrive",
  meta: [
    {
      name: "NohamDrive | Echo",
      content:
        "Discover a new way to browse your files on the web directly on a terminal-like interface",
    },
  ],
});

useSeoMeta({
  description:
    "Discover a new way to browse your files on the web directly on a terminal-like interface",
  ogTitle: "Echo - NohamDrive",
  ogDescription:
    "Discover a new way to browse your files on the web directly on a terminal-like interface",
  ogImage: "[og:image]",
  ogUrl: "[og:url]",
  twitterTitle: "Echo - NohamDrive",
  twitterDescription:
    "Discover a new way to browse your files on the web directly on a terminal-like interface",
  twitterImage: "[twitter:image]",
  twitterCard: "summary",
});
</script>

<template>
  <Terminal />
</template>
