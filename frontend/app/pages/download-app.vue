<script lang="ts" setup>
import type { ButtonProps } from "@nuxt/ui";

const links = ref<ButtonProps[]>([
  {
    label: "Download App for windows",
    color: "primary",
    variant: "outline",
    leadingIcon: "desktop:microsoft-icon",
    to: "https://github.com/NoArAlMa/NohamDrive/releases/latest/download/NohamDrive-Setup.exe",
    target: "_blank",
  },
  {
    label: "Download App for Mac",
    color: "neutral",
    variant: "outline",
    leadingIcon: "file-icons:apple",
    to: "https://www.apple.com/fr/",
    target: "_blank",
  },
]);
</script>

<template>
  <UPageCTA
    class="w-full h-full flex items-center justify-center"
    title="Télécharge notre application !!"
    description="On fait une app alors pourquoi pas la télécharger hein ?"
    variant="soft"
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
