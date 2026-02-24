<script lang="ts" setup>
const { isMobile } = useResponsive();
</script>

<template>
  <LazyUApp>
    <LazyUDashboardGroup>
      <ClientOnly>
        <LazyNavigationSidebar />
      </ClientOnly>
      <LazyUDashboardPanel :ui="{ body: 'p-0 laptop:p-4' }">
        <template #header>
          <div class="lg:hidden p-4 border-b">
            <LazyUDashboardSidebarToggle variant="subtle" label="Menu" />
          </div>
        </template>

        <template #body>
          <LazyUDashboardSearch />
          <NuxtPage />
        </template>
      </LazyUDashboardPanel>
    </LazyUDashboardGroup>
  </LazyUApp>
</template>
