<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import type { DropdownMenuItem } from "@nuxt/ui";

const itemsDropDown = ref<DropdownMenuItem[]>([
  {
    label: "Log out",
    icon: "material-symbols:logout-rounded",
    color: "error",
    click: () => {},
  },
  {
    type: "separator",
  },
  {
    label: "Settings",
    icon: "material-symbols:settings-outline-rounded",
  },
  {
    label: "Inbox",

    icon: "material-symbols:inbox-outline-rounded",
  },
  {
    label: "My account",
    icon: "material-symbols:person-outline-rounded",
  },
]);

const items: NavigationMenuItem[][] = [
  [
    {
      label: "Home",
      icon: "i-lucide-house",
      tooltip: true,
      to: "/",
    },
    {
      label: "My files",
      icon: "material-symbols:folder-copy-outline-rounded",
      tooltip: true,
      to: "/explorer",
    },
    {
      label: "Contacts",
      icon: "material-symbols:person-outline-rounded",
      tooltip: true,
    },
    {
      label: "Teams",
      icon: "material-symbols:groups-outline-rounded",
      tooltip: true,
      children: [
        {
          label: "Teams1",
        },
        {
          label: "Teams2",
        },
        {
          label: "Teams3",
        },
      ],
    },
  ],
  [
    {
      label: "Report a bug",
      icon: "i-lucide-info",
      onSelect: () => {},
      tooltip: true,
    },
  ],
];
</script>

<template>
  <UDashboardSidebar
    collapsible
    :ui="{
      root: 'border-e-0 transition-[width] duration-300 ease-in-out ',
      header: 'transition-[padding,opacity] duration-200',
      body: 'transition-[padding] duration-200',
      footer: 'transition-[padding] duration-200 border-t border-default',
    }"
    class="min-w-fit overflow-hidden"
  >
    <template #header="{ collapsed }">
      <div class="w-full flex justify-start items-center">
        <h1
          v-show="!collapsed"
          class="mr-auto pr-4 text-primary font-bold select-none whitespace-nowrap overflow-hidden text-ellipsis transition-all duration-200 text-sm tablet:text-base laptop:text-lg desktop:text-xl"
        >
          NohamDrive
        </h1>

        <UDashboardSidebarCollapse variant="ghost" :block="collapsed" />
      </div>
    </template>

    <template #default="{ collapsed }">
      <UDashboardSearchButton
        :collapsed="collapsed"
        :block="collapsed"
        :square="collapsed"
        class="mb-3"
        :ui="{
          base: [
            'transition-all duration-200',
            'text-sm tablet:text-base',
            collapsed
              ? 'px-2 py-1.5 justify-center'
              : 'px-2 py-1.5 tablet:px-3 tablet:py-2',
          ].join(' '),
        }"
      />

      <!-- Menu principal -->
      <div class="overflow-y-scroll no-scrollbar">
        <UNavigationMenu
          :collapsed="collapsed"
          :items="items[0]"
          orientation="vertical"
          :ui="{
            link: [
              'group relative flex items-center rounded-lg',
              'whitespace-nowrap overflow-hidden',
              'transition-all duration-200',
              collapsed
                ? 'justify-center px-2 py-2'
                : 'px-3 py-2.5 tablet:px-4 tablet:py-3',
              'text-sm tablet:text-base',
            ].join(' '),

            linkLeadingIcon: [
              'shrink-0 transition-all duration-200',
              collapsed ? 'size-5' : 'size-4 tablet:size-5',
            ].join(' '),
          }"
        />
      </div>

      <!-- Menu secondaire -->
      <UNavigationMenu
        :collapsed="collapsed"
        :items="items[1]"
        orientation="vertical"
        class="mt-auto pt-2"
        :ui="{
          link: [
            'group relative flex items-center rounded-lg',
            'whitespace-nowrap overflow-hidden',
            'transition-all duration-200',
            collapsed
              ? 'justify-center px-2 py-2'
              : 'px-3 py-2.5 tablet:px-4 tablet:py-3',
            'text-sm tablet:text-base',
          ].join(' '),

          linkLeadingIcon: [
            'shrink-0 transition-all duration-200',
            collapsed ? 'size-5' : 'size-4 tablet:size-5',
          ].join(' '),
        }"
      />
    </template>

    <template #footer="{ collapsed }">
      <UDropdownMenu
        :items="itemsDropDown"
        :content="{
          align: 'start',
          side: 'top',
          sideOffset: 2,
        }"
        :ui="{ content: 'w-(--reka-dropdown-menu-trigger-width)' }"
        class="w-full"
      >
        <UButton
          :avatar="{
            src: 'https://github.com/Karssou.png',
            size: 'md',
          }"
          :label="collapsed ? undefined : 'Username'"
          color="neutral"
          variant="ghost"
          class="w-full"
          :block="collapsed"
          :ui="{
            label: 'mr-auto',
          }"
        >
        </UButton>
      </UDropdownMenu>
    </template>
  </UDashboardSidebar>
</template>
