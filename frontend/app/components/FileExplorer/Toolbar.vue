<script lang="ts" setup>
import type { DropdownMenuItem, NavigationMenuItem } from "@nuxt/ui";

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
    label: "Télécharger",
    icon: "material-symbols:download-rounded",

    handler: () =>
      runBatch(props.items, action.download, {
        loading: "Téléchargement en cours...",
        success: "Téléchargement terminé !",
        error: "Le téléchargement a échoué",
      }),
  },
  {
    key: "move",
    label: "Déplacer",
    icon: "material-symbols:drive-file-move-outline-rounded",
    disabled: true,

    handler: () => {},
  },
  {
    key: "share",
    label: "Partager",
    icon: "material-symbols:share-windows-rounded",
    disabled: true,

    handler: () => {},
  },
  {
    key: "delete",
    label: "Supprimer",
    icon: "material-symbols:delete-outline-rounded",
    color: "error",
    handler: () =>
      runBatch(props.items, action.del, {
        loading: "Suppression en cours…",
        success: "Éléments supprimés !",
        error: "Erreur lors de la suppression",
      }),
  },
]);

const DropdownItems = ref<DropdownMenuItem[]>([
  {
    label: "Compresser",
    icon: "material-symbols:compress-rounded",
    onSelect: () => action.compress(props.items),
  },
]);

const DrawerItems = ref<NavigationMenuItem[]>([
  [
    {
      label: "Télécharger",
      icon: "material-symbols:download-rounded",
      onSelect: () => {
        runBatch(props.items, action.download);
      },
    },
    {
      label: "Déplacer",
      icon: "material-symbols:drive-file-move-outline-rounded",
      disabled: true,
      onSelect: () => {},
    },
    {
      slot: "suppress",
    },
  ],
  [
    {
      label: "Partager",
      icon: "material-symbols:share-windows-rounded",
      disabled: true,
      onSelect: () => {},
    },

    {
      label: "Compresser",
      icon: "material-symbols:compress-rounded",
      onSelect: () => action.compress(props.items),
    },
  ],
]);
</script>

<template>
  <ClientOnly>
    <Transition name="slide-fade" appear>
      <section
        v-if="!isMobile"
        class="flex justify-start gap-2 w-full h-full shadow-sm rounded-md"
      >
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
              label="Plus"
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
            color="neutral"
            variant="subtle"
            icon="material-symbols:tools-wrench-outline-rounded"
          />

          <template #body>
            <UNavigationMenu :items="DrawerItems" orientation="vertical">
              <template #suppress>
                <UButton
                  leading-icon="material-symbols:delete-outline-rounded"
                  label="Supprimer"
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
