<script lang="ts" setup>
const { isMobile } = useResponsive();
</script>

<template>
  <UApp>
    <UDashboardGroup>
      <ClientOnly>
        <NavigationSidebar />
      </ClientOnly>
      <UDashboardPanel :ui="{ body: 'p-0 laptop:p-4' }">
        <template #header>
          <div class="lg:hidden p-4 border-b">
            <UDashboardSidebarToggle variant="subtle" label="Menu" />
          </div>
        </template>

        <template #body>
          <UDashboardSearch />
          <NuxtPage />
        </template>
      </UDashboardPanel>
    </UDashboardGroup>
  </UApp>
</template>
