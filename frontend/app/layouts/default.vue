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
          <LazyUDashboardSearch />
          <NuxtPage />
        </template>
      </LazyUDashboardPanel>
    </LazyUDashboardGroup>
  </LazyUApp>
</template>
