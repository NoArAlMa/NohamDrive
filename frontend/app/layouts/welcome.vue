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
      label: "Review",
      icon: "i-lucide-database",
    },
    {
      label: "Echo",
      icon: "mdi:star-four-points-outline",
      ui: {
        linkLeadingIcon: "text-secondary",
      },
      to: "#echo",

      class: "font-semibold text-secondary",
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
              <NuxtLink to="/home" class="">
                <h1 class="text-primary font-bold text-2xl">NohamDrive</h1>
              </NuxtLink>
            </template>

            <UNavigationMenu :items="items" />

            <template #right>
              <UButton label="Connexion" variant="ghost" color="neutral" />
              <UButton color="primary" variant="subtle">S’inscrire</UButton>
              <UButton
                icon="mdi:github"
                variant="ghost"
                color="neutral"
                to="https://github.com/NoArAlMa/NohamDrive"
                target="_blank"
              />
            </template>
          </UDashboardNavbar>
        </template>

        <template #body>
          <NuxtPage />
        </template>
      </UDashboardPanel>
    </UDashboardGroup>
  </UApp>
</template>
