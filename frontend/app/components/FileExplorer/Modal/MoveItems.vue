<script lang="ts" setup>
const { currentPath } = useFSStore();
const { runBatch } = useBatchAction();
const { move } = useFsActions();

const props = defineProps<{
  items: ApiFileItem[];
}>();

const emit = defineEmits<{ close: [any] }>();

const breadcrumb = ref(currentPath);

function close() {
  emit("close", "");
}

const listNames = computed(() => {
  const names = props.items.map((i) => i.name);

  if (names.length <= 5) {
    return names.join("\n");
  }

  return [...names.slice(0, 5), `+ ${names.length - 5} autres...`].join("\n");
});

const itemsCount = props.items.length;

const data = ref<GenericAPIResponse<ApiFileTreeData> | null>(null);
const loading = ref(false);
const error = ref<Error | null>(null);

const fetchFileTree = async (): Promise<void> => {
  if (loading.value) return;

  try {
    loading.value = true;
    error.value = null;

    const response = await $fetch<GenericAPIResponse<ApiFileTreeData>>(
      "/storage/tree",
      {
        params: { path: breadcrumb.value },
      },
    );

    data.value = response;
  } catch (err) {
    error.value = err as Error;
  } finally {
    loading.value = false;
  }
};

watch(
  () => breadcrumb.value,
  () => fetchFileTree(),
  { immediate: true },
);

const navigate = (inputPath: string) => {
  if (loading.value) return;

  const newPath = resolvePath(inputPath, breadcrumb.value);

  if (newPath === breadcrumb.value) return;

  breadcrumb.value = newPath;
};

const tree = computed<ApiFileItem[]>(() => {
  return data.value?.data?.items.filter((item) => item.is_dir) ?? [];
});

const generateBreadcrumbItems = () => {
  const parts = breadcrumb.value.split("/").filter((part) => part !== "");
  const items = parts.map((part, index) => {
    const pathSoFar = "/" + parts.slice(0, index + 1).join("/");
    return {
      label: part,
      path: pathSoFar,
    };
  });

  // Ajoute toujours la racine ("/") en premier
  return [
    {
      label: "Mes fichiers",
      path: "/",
    },
    ...items,
  ];
};

const items = computed(() => {
  return generateBreadcrumbItems();
});

async function moveItems() {
  const destination = breadcrumb.value;

  if (!props.items.length) return;

  await runBatch(
    props.items,
    async (item, options) => {
      const sourcePath = item.is_dir
        ? joinPath(currentPath, item.name) + "/"
        : joinPath(currentPath, item.name);

      await move(sourcePath, destination, options);
    },
    {
      loading: "Déplacement en cours...",
      success: "Déplacement terminé !",
      error: "Le déplacement a échoué",
    },
  );

  close();
}
</script>
<template>
  <UModal
    title="Move Items"
    description="Choisissez un dossier de destination"
    class="min-w-[50vw] h-2/3"
  >
    <template #body>
      <div
        class="w-full h-full flex flex-col gap-1 justify-between overflow-hidden"
      >
        <div>
          <LazyUBreadcrumb
            :items="items"
            overflow="ellipsis"
            :max-items="4"
            class="mb-2"
            :ui="{
              root: '',
              list: 'flex items-center gap-0.5 min-w-0',
              item: 'min-w-0',
              link: 'group flex items-center gap-1 truncate',
            }"
          >
            <template #separator>
              <span class="text-muted shrink-0">/</span>
            </template>
            <template #item="{ item }">
              <LazyULink
                class="mx-0 px-2 py-1 rounded-md hover:bg-elevated truncate max-w-40"
                :title="item.label"
                :disabled="loading"
                @click="navigate(item.path)"
              >
                {{ item.label }}
              </LazyULink>
            </template>
          </LazyUBreadcrumb>
          <div class="flex flex-row justify-center">
            <div class="w-[95vw] mx-auto border-b border-muted/50"></div>
          </div>
        </div>

        <!-- Loader -->
        <div class="w-full h-full">
          <div v-if="loading" class="w-full h-full">
            <LazyFileExplorerLoaderList />
          </div>
          <div
            v-if="tree.length === 0"
            class="w-full h-full flex items-center justify-center"
          >
            <LazyUEmpty
              class="w-full tablet:w-fit min-w-125"
              variant="soft"
              icon="material-symbols:sad-tab-outline-rounded"
              title="No folders"
              description="It looks like you haven't added any files/folders. Create one to get started."
              size="xl"
              :actions="[
                {
                  icon: 'material-symbols:keyboard-return-rounded',
                  label: 'Return',
                  color: 'neutral',
                  variant: 'soft',
                  size: 'md',
                  loadingAuto: true,
                  onClick: () => navigate('..'),
                },
              ]"
            />
          </div>

          <div
            v-else
            class="w-full h-full flex flex-col overflow-y-auto overflow-x-hidden divide-y divide-neutral-800"
          >
            <div
              v-for="row in tree"
              :key="row.name"
              class="flex items-center px-2 py-2.5 cursor-pointer transition-colors duration-75 hover:bg-neutral-800"
            >
              <LazyUIcon
                name="explorer:folder-icon"
                class="text-lg mr-2 shrink-0"
              />
              <LazyULink draggable="false" class="min-w-0">
                <span
                  draggable="false"
                  class="block truncate cursor-pointer"
                  @click="navigate(row.name)"
                  :title="row.name"
                >
                  {{ row.name }}
                </span>
              </LazyULink>
            </div>
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex items-center gap-2 w-full">
        <LazyUPopover
          mode="hover"
          :open-delay="100"
          :close-delay="100"
          :content="{
            align: 'center',
            side: 'top',
            sideOffset: 8,
          }"
        >
          <span class="mr-auto text-sm font-semibold">
            {{ itemsCount }} éléments sélectionné
          </span>

          <template #content>
            <div
              class="max-h-60 flex gap-y-2 px-2 py-1 overflow-y-auto whitespace-pre text-xs"
            >
              {{ listNames }}
            </div>
          </template>
        </LazyUPopover>
        <UButton
          label="Annuler"
          variant="ghost"
          color="neutral"
          @click="close"
        />

        <UButton
          label="Déplacer ici"
          color="primary"
          variant="subtle"
          class="hover:cursor-pointer"
          loading-auto
          :disabled="breadcrumb === currentPath"
          @click="moveItems"
        />
      </div>
    </template>
  </UModal>
</template>
