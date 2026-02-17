<template>
  <UApp>
    <UDashboardGroup>
      <ClientOnly>
        <NavigationSidebar />
      </ClientOnly>
      <UDashboardPanel>
        <template #header>
          <div class="lg:hidden p-4 border-b">
            <UDashboardSidebarToggle variant="subtle" />
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
