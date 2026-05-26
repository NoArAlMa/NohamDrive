<script lang="ts" setup>
const { isMobile } = useResponsive();
const { switchLocale, $getLocale } = useI18n();
const locale = computed(() => $getLocale());

const groups = computed(() => [
  {
    id: "navigation",
    label: "Navigation",
    items: [
      {
        label: "Home",
        icon: "i-heroicons-home",
        onSelect: () => navigateTo("/"),
      },
      {
        label: "Settings",
        icon: "i-heroicons-cog-6-tooth",
        onSelect: () => navigateTo("/settings"),
      },
    ],
  },

  {
    id: "language",
    label: "Language",
    items: [
      {
        label: "Français",
        icon: "flag:fr-4x3",
        active: locale.value === "fr",
        onSelect: () => switchLocale("fr"),
      },
      {
        label: "English",
        icon: "flag:gb-4x3",
        active: locale.value === "en",
        onSelect: () => switchLocale("en"),
      },
    ],
  },
]);
</script>

<template>
  <UApp>
    <UDashboardGroup>
      <ClientOnly>
        <LazyNavigationSidebar />
      </ClientOnly>
      <UDashboardPanel :ui="{ body: 'p-0 laptop:p-4' }">
        <template #header>
          <div class="lg:hidden">
            <div class="flex justify-between items-center p-3">
              <h1
                class="text-primary font-bold select-none whitespace-nowrap overflow-hidden text-ellipsis text-lg"
              >
                NohamDrive
              </h1>

              <LazyUDashboardSidebarToggle
                size="lg"
                variant="ghost"
                icon="material-symbols:menu-rounded"
              />
            </div>

            <div class="w-[95vw] mx-auto border-b border-muted/50"></div>
          </div>
        </template>

        <template #body>
          <LazyUDashboardSearch :groups="groups" />
          <NuxtPage />
        </template>
      </UDashboardPanel>
    </UDashboardGroup>
  </UApp>
</template>
