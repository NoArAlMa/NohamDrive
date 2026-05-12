<script lang="ts" setup>
import type { DropdownMenuItem, NavigationMenuItem } from "@nuxt/ui";
import { LazyFileExplorerModalMoveItems } from "#components";

const { t } = useI18n();

const props = defineProps<{
  items: ApiFileItem[];
}>();
const { isMobile } = useResponsive();
const isDrawerOpen = ref(false);
const action = useFsActions();
const { runBatch } = useBatchAction();

type FileAction = {
  key: string;
  label: string;
  icon: string;
  color?: "neutral" | "error";
  disabled?: boolean;
  group?: "main" | "secondary" | "danger";
  handler: () => void;
};

const fileActions = computed<FileAction[]>(() => [
  {
    key: "download",
    label: t("fileExplorer.download") as string,
    icon: "material-symbols:download-rounded",

    handler: () =>
      runBatch(props.items, action.download, {
        loading: t("fileExplorer.downloading") as string,
        success: t("fileExplorer.downloadSuccess") as string,
        error: t("fileExplorer.downloadError") as string,
      }),
  },
  {
    key: "move",
    label: t("fileExplorer.move") as string,
    icon: "material-symbols:drive-file-move-outline-rounded",
    handler: async () => {
      const overlay = useOverlay();
      const MoveModal = overlay.create(LazyFileExplorerModalMoveItems, {
        props: {
          items: props.items,
        },
      });
      const modal = MoveModal.open();
      const result = await modal.result;
    },
  },
  {
    key: "share",
    label: t("fileExplorer.share") as string,
    icon: "material-symbols:share-windows-rounded",
    disabled: true,

    handler: () => {},
  },
  {
    key: "delete",
    label: t("fileExplorer.delete") as string,
    icon: "material-symbols:delete-outline-rounded",
    color: "error",
    handler: () =>
      runBatch(props.items, action.del, {
        loading: t("fileExplorer.deleting") as string,
        success: t("fileExplorer.deleteSuccess") as string,
        error: t("fileExplorer.deleteError") as string,
      }),
  },
]);

const DropdownItems = computed<DropdownMenuItem[]>(() => [
  {
    label: t("fileExplorer.compress") as string,
    icon: "material-symbols:compress-rounded",
    onSelect: () => action.compress(props.items),
  },
]);

const DrawerItems = computed<NavigationMenuItem[]>(() => [
  [
    {
      label: t("fileExplorer.download") as string,
      icon: "material-symbols:download-rounded",
      onSelect: () => {
        runBatch(props.items, action.download);
      },
    },
    {
      slot: "suppress",
    },
  ],
  [
    {
      label: t("fileExplorer.share") as string,
      icon: "material-symbols:share-windows-rounded",
      disabled: true,
      onSelect: () => {},
    },

    {
      label: t("fileExplorer.compress") as string,
      icon: "material-symbols:compress-rounded",
      onSelect: () => action.compress(props.items),
    },
  ],
]);
</script>

<template>
  <ClientOnly>
    <Transition name="slide-fade" appear>
      <section v-if="!isMobile" class="flex justify-start gap-2 w-full h-full">
        <div>
          <UButton
            v-for="action in fileActions"
            :key="action.key"
            :leading-icon="action.icon"
            :label="action.label"
            :color="action.color ?? 'neutral'"
            variant="ghost"
            size="lg"
            class="px-2 py-1"
            :disabled="action.disabled"
            @click="action.handler"
            loading-auto
          />

          <UDropdownMenu :items="DropdownItems" class="ml-3">
            <UButton
              leading-icon="material-symbols:more-horiz"
              :label="String(t('fileExplorer.more'))"
              color="neutral"
              variant="ghost"
              class="px-2 py-1 ml-3"
            />
          </UDropdownMenu>
        </div>
      </section>
      <section v-else>
        <UDrawer v-model:open="isDrawerOpen">
          <UButton
            color="secondary"
            variant="subtle"
            icon="material-symbols:tools-wrench-outline-rounded"
          />

          <template #body>
            <UNavigationMenu :items="DrawerItems" orientation="vertical">
              <template #suppress>
                <UButton
                  leading-icon="material-symbols:delete-outline-rounded"
                  :label="String(t('fileExplorer.delete'))"
                  color="error"
                  class="p-0"
                  variant="link"
                  @click="runBatch(props.items, action.del)"
                />
              </template>
            </UNavigationMenu>
          </template>
        </UDrawer>
      </section>
    </Transition>
  </ClientOnly>
</template>

<style scoped>
.slide-fade-enter-from,
.slide-fade-appear-from {
  opacity: 0;
  transform: translateY(12px);
}

.slide-fade-enter-to,
.slide-fade-appear-to {
  opacity: 1;
  transform: translateY(0);
}

.slide-fade-enter-active,
.slide-fade-appear-active {
  transition:
    opacity 200ms ease-out,
    transform 200ms ease-out;
}
</style>
