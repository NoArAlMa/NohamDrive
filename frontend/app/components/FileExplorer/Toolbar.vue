<script lang="ts" setup>
import type { DropdownMenuItem } from "@nuxt/ui";

const props = defineProps<{
  items: ApiFileItem[];
}>();

const action = useFsActions();
const { runBatch } = useBatchAction();

const DropdownItems = ref<DropdownMenuItem[]>([
  {
    label: "Compresser",
    icon: "material-symbols:compress-rounded",
    onSelect: () => action.compress(props.items),
  },
]);
</script>

<template>
  <ClientOnly>
    <Transition name="slide-fade" appear>
      <section
        class="px-4 py-2 flex justify-between gap-2 w-full h-full shadow-sm rounded-xl"
      >
        <div>
          <UButton
            leading-icon="material-symbols:share-windows-rounded"
            label="Partager"
            color="neutral"
            variant="ghost"
            class="px-2 py-1"
            disabled
            @click=""
          />

          <UButton
            leading-icon="material-symbols:download-rounded"
            label="Télécharger"
            color="neutral"
            variant="ghost"
            class="px-2 py-1"
            @click="
              runBatch(props.items, action.download, {
                loading: 'Téléchargement en cours...',
                success: 'Téléchargement terminé !',
                error: 'Le téléchargement à échoué',
              })
            "
          />
          <UButton
            leading-icon="material-symbols:drive-file-move-outline-rounded"
            label="Déplacer"
            color="neutral"
            variant="ghost"
            disabled
            class="px-2 py-1"
          />
          <UButton
            leading-icon="material-symbols:delete-outline-rounded"
            label="Supprimer"
            color="error"
            variant="ghost"
            class="px-2 py-1"
            @click="
              runBatch(props.items, action.del, {
                loading: 'Suppression en cours…',
                success: 'Éléments supprimés !',
                error: 'Erreur lors de la suppression',
              })
            "
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
