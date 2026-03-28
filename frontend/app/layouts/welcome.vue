<script lang="ts" setup>
import type { NavigationMenuItem } from "@nuxt/ui";

const { isMobile } = useResponsive();

const items = ref<NavigationMenuItem[][]>([
  [
    {
      label: "Features",
      icon: "material-symbols:layers-outline-rounded",
      to: "#features",
    },
    {
      label: "Echo",
      icon: "terminal:echo-icon",
      ui: {
        linkLeadingIcon: "text-secondary",
      },
      to: "#echo",
      class: "font-semibold text-secondary",
    },
    {
      label: "Review",
      icon: "material-symbols:comment-outline-rounded",
      to: "#testimonials",
    },
  ],
]);
</script>

<template>
  <UApp>
    <UDashboardGroup>
      <UDashboardPanel
        :ui="{
          body: 'p-0',
        }"
      >
        <template #header>
          <UDashboardNavbar toggle>
            <template #title>
              <h1 class="text-primary font-bold text-2xl">NohamDrive</h1>
            </template>

            <UNavigationMenu :items="items" />

            <template #right>
              <div class="mr-3 flex gap-2">
                <UButton
                  icon="material-symbols:login-rounded"
                  label="Log in"
                  variant="ghost"
                  color="neutral"
                  loading-auto
                  @click="navigateTo('/auth?mode=login')"
                />
                <UButton
                  label="Register"
                  color="primary"
                  variant="subtle"
                  @click="navigateTo('/auth?mode=register')"
                  loading-auto
                />
              </div>
            </template>
          </UDashboardNavbar>
        </template>

        <template #body>
          <NuxtPage />
        </template>

        <template #footer>
          <UFooter class="py-0" v-if="!isMobile">
            <template #left>
              <div
                class="flex items-center gap-2 text-sm text-muted select-none"
              >
                <span>Built with</span>

                <UIcon
                  name="logos:nuxt-icon"
                  class="size-5"
                  aria-label="Nuxt"
                />

                <UIcon
                  name="logos:tailwindcss-icon"
                  class="size-5"
                  aria-label="TailwindCSS"
                />
              </div>
            </template>

            <div class="flex flex-col items-center select-none">
              <h1 class="text-lg font-bold text-primary tracking-tight">
                NohamDrive
              </h1>
              <span class="text-xs text-muted"> Next level file storage </span>
            </div>

            <template #right>
              <div class="flex items-center gap-3 text-sm text-muted">
                <span> © {{ new Date().getFullYear() }} Karssou </span>

                <UButton
                  icon="mdi:github"
                  color="neutral"
                  variant="ghost"
                  to="https://github.com/NoArAlMa/NohamDrive"
                  target="_blank"
                  aria-label="GitHub repository"
                />
              </div>
            </template>
          </UFooter>
        </template>
      </UDashboardPanel>
    </UDashboardGroup>
  </UApp>
</template>
