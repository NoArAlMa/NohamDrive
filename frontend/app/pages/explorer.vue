<script setup lang="ts">
useHead({
  title: "File Explorer - NohamDrive",
  meta: [
    {
      name: "NohamDrive | File Explorer",
      content:
        "Browse your file stored in the cloud directly in this file explorer",
    },
  ],
});

useSeoMeta({
  description:
    "Browse your file stored in the cloud directly in this file explorer",
  ogTitle: "File Explorer - NohamDrive",
  ogDescription:
    "Browse your file stored in the cloud directly in this file explorer",
  ogImage: "[og:image]",
  ogUrl: "[og:url]",
  twitterTitle: "File Explorer - NohamDrive",
  twitterDescription:
    "Browse your file stored in the cloud directly in this file explorer",
  twitterImage: "[twitter:image]",
  twitterCard: "summary",
});
</script>

<template>
  <section
    class="flex flex-1 overflow-hidden md:items-center md:justify-center md:px-4 md:py-6"
  >
    <div
      class="w-full h-full flex flex-col overflow-hidden md:max-w-7xl md:h-[80vh] md:rounded-md md:shadow-lg desktop:max-h-9/12"
    >
      <FileExplorerContainer class="flex-1 overflow-auto" />
    </div>
  </section>
</template>
