<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import type { DropdownMenuItem } from "@nuxt/ui";

const { isMobile } = useResponsive();

const { isElectron } = useElectron();

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
    [
      {
        label: "Home",
        icon: "i-lucide-house",
        to: "/home",
      },
      {
        label: "My files",
        icon: "material-symbols:folder-copy-outline-rounded",
        to: "/explorer",
      },
      {
        label: "Contacts",
        icon: "material-symbols:person-outline-rounded",
      },
      {
        label: "Teams",
        icon: "material-symbols:groups-outline-rounded",
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
        label: "Echo",
        icon: "mdi:star-four-points-outline",
        to: "/terminal",
      },
    ],
  ],
  [
    ...(isElectron.value === false
      ? [
          {
            label: "Download desktop app",
            icon: "material-symbols:download-2-outline-rounded",
            to: "/download-app",
            tooltip: true,
          },
        ]
      : []),
    {
      label: "Report a bug",
      icon: "i-lucide-info",
      to: "https://c.tenor.com/e3OI7DDT9i0AAAAd/tenor.gif",
      target: "_blank",
      tooltip: true,
    },
  ],
];
const collapsed = ref(false);
</script>

<template>
  <UDashboardSidebar
    v-model:collapsed="collapsed"
    mode="drawer"
    toggle-side="right"
    collapsible
    :ui="{
      root: 'border-e-0 transition-[width] duration-300 ease-in-out',
      header: 'transition-[padding,opacity] duration-200',
      body: 'transition-[padding] duration-200',
      footer: 'transition-[padding] duration-200 border-t border-default',
    }"
    :class="collapsed ? '' : 'min-w-fit max-w-70'"
  >
    <template #header>
      <div class="w-full flex justify-start items-center">
        <h1
          v-show="!collapsed && !isMobile"
          class="mr-auto pr-4 text-primary font-bold select-none whitespace-nowrap overflow-hidden text-ellipsis transition-all duration-200 text-sm tablet:text-base laptop:text-lg desktop:text-2xl"
        >
          NohamDrive
        </h1>

        <UDashboardSidebarCollapse variant="ghost" :block="collapsed" />
      </div>
    </template>

    <template #default>
      <UDashboardSearchButton
        v-if="!isMobile"
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
      <div class="overflow-y-auto">
        <UNavigationMenu
          tooltip
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
        >
          <template #list-leading></template>
        </UNavigationMenu>
      </div>

      <!-- Menu secondaire -->
      <UNavigationMenu
        v-if="!isMobile"
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
              ? 'justify-center px-2 py-1.5'
              : 'px-2 py-1.5 tablet:px-4 tablet:py-3',
            'text-sm tablet:text-base',
          ].join(' '),

          linkLeadingIcon: [
            'shrink-0 transition-all duration-200',
            collapsed ? 'size-4' : 'size-3 tablet:size-4',
          ].join(' '),
        }"
      />
    </template>

    <template #footer>
      <UDropdownMenu
        :items="itemsDropDown"
        :content="{
          align: 'start',
          side: 'top',
          sideOffset: 2,
        }"
        :ui="{ content: 'w-(--reka-dropdown-menu-trigger-width)' }"
        :class="collapsed ? '' : 'w-full'"
      >
        <UButton
          :avatar="{
            src: 'https://i.pinimg.com/736x/be/a3/49/bea3491915571d34a026753f4a872000.jpg',
            size: 'md',
          }"
          :label="collapsed ? undefined : 'Username'"
          color="neutral"
          variant="ghost"
          :square="false"
          :block="collapsed"
          :class="
            collapsed
              ? 'size-10 flex items-center justify-center mx-auto'
              : 'w-full'
          "
          :ui="{
            label: 'ml-1',
          }"
        >
        </UButton>
      </UDropdownMenu>
    </template>
  </UDashboardSidebar>
</template>
