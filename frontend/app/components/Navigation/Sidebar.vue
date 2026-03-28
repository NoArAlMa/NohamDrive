<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import type { DropdownMenuItem } from "@nuxt/ui";
import Limiter from "./Limiter.vue";

const { isMobile } = useResponsive();
const { user } = useAuthStore();
const { logoutUser } = useAuth();

const name_user = user?.full_name;

const { isElectron } = useElectron();

const itemsDropDown = ref<DropdownMenuItem[]>([
  {
    label: "Log out",
    icon: "material-symbols:logout-rounded",
    color: "error",
    onSelect: () => logoutUser(),
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
        icon: "terminal:echo-icon",
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
  <LazyUDashboardSidebar
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

        <LazyUDashboardSidebarCollapse variant="ghost" :block="collapsed" />
      </div>
    </template>

    <template #default>
      <LazyUDashboardSearchButton
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
              : 'px-2 py-1.5 tablet:px-2 tablet:py-1.5',
          ].join(' '),
        }"
      />

      <!-- Menu principal -->
      <div class="overflow-y-auto mb-auto">
        <LazyUNavigationMenu
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
        </LazyUNavigationMenu>
      </div>
      <div
        class="flex gap-1 m-0"
        :class="collapsed ? 'flex-col items-center' : 'flex-row'"
        v-if="!isMobile"
      >
        <UTooltip
          text="Download app"
          :content="{
            side: 'top',
          }"
          :delay-duration="10"
        >
          <UButton
            v-if="!isElectron"
            icon="material-symbols:download-2-outline-rounded"
            to="/download-app"
            variant="ghost"
            size="sm"
            color="neutral"
          />
        </UTooltip>
        <UTooltip
          text="Report a bug"
          :content="{
            side: 'top',
          }"
          :delay-duration="10"
        >
          <UButton
            icon="i-lucide-info"
            target="_blank"
            to="https://c.tenor.com/e3OI7DDT9i0AAAAd/tenor.gif"
            variant="ghost"
            size="sm"
            color="neutral"
            class="transition-all duration-200 hover:text-error"
          />
        </UTooltip>
      </div>
      <Limiter v-if="!collapsed" class="-mt-2.5" />
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
          :label="collapsed ? 'undefined' : name_user ? name_user : 'Salut nom'"
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
  </LazyUDashboardSidebar>
</template>
