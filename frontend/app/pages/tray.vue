<script lang="ts" setup>
import type { DropdownMenuItem } from "@nuxt/ui";

definePageMeta({
  layout: false,
  middleware: "electron-middleware",
});

type LocalItem = {
  id: string;
  name: string;
  kind: "file" | "folder";
  path: string;
  parentPath: string;
};

const drivePath = ref("");
const selectedId = ref<string | null>(null);
const search = ref("");
const localItems = ref<LocalItem[]>([]);
const currentPath = ref("");

const syncer = useSyncState();

const dropdownItems = computed(
  () =>
    [
      {
        label: "Refresh Files",
        icon: "material-symbols:refresh-rounded",
        onSelect: () => loadFiles(),
      },
      {
        label: "Settings",
        icon: "material-symbols:settings-outline-rounded",
      },
      {
        label: syncer.enabled.value ? "Stop Sync" : "Resume Sync",
        icon: syncer.enabled.value
          ? "material-symbols:cloud-off-outline-rounded"
          : "material-symbols:play-arrow-rounded",
        color: syncer.enabled.value ? "error" : "primary",
        disabled: syncer.loading.value,
        onSelect: async () => {
          await syncer.toggle();
        },
      },
    ] satisfies DropdownMenuItem[],
);

const visibleItems = computed(() => {
  const query = search.value.toLowerCase().trim();

  return localItems.value
    .filter((item) => item.parentPath === currentPath.value)
    .filter((item) => {
      if (!query) return true;
      return item.name.toLowerCase().includes(query);
    })
    .sort((a, b) => {
      if (a.kind !== b.kind) {
        return a.kind === "folder" ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });
});

const selectedItem = computed(() => {
  return localItems.value.find((item) => item.id === selectedId.value);
});

const syncedCount = computed(() => {
  return localItems.value.length;
});

const canGoUp = computed(() => {
  return currentPath.value !== drivePath.value;
});

const displayPathSegments = computed(() => {
  const parts = currentPath.value
    .replace(/\\/g, "/")
    .split("/")
    .filter(Boolean);

  if (parts.length <= 3) return parts;
  return ["…", ...parts.slice(-2)];
});

function openItem(item: LocalItem) {
  if (item.kind === "folder") {
    currentPath.value = item.path;
  }
}

function goUp() {
  if (!canGoUp.value) return;
  const parts = currentPath.value.split("/");
  parts.pop();
  currentPath.value = parts.join("/");
}

function buildItems(payload: { folder: string; files: string[] }) {
  const base = payload.folder.replace(/\\/g, "/");
  const items: LocalItem[] = [];
  const addedFolders = new Set<string>();

  for (const rawFile of payload.files) {
    const clean = rawFile.replace(/\\/g, "/").replace(/^\//, "");
    const parts = clean.split("/");
    let currentParent = base;

    for (let i = 0; i < parts.length - 1; i++) {
      const folderName = parts[i];
      const folderPath = `${currentParent}/${folderName}`;

      if (!addedFolders.has(folderPath)) {
        items.push({
          id: folderPath,
          name: folderName!,
          kind: "folder",
          path: folderPath,
          parentPath: currentParent,
        });
        addedFolders.add(folderPath);
      }
      currentParent = folderPath;
    }

    // Création du fichier
    const fileName = parts.at(-1)!;
    const filePath = `${currentParent}/${fileName}`;

    items.push({
      id: filePath,
      name: fileName,
      kind: "file",
      path: filePath,
      parentPath: currentParent,
    });
  }

  return items;
}

async function loadFiles() {
  try {
    const res = await $fetch<{ folder: string; files: string[] }>(
      "/api/syncer/files",
    );
    localItems.value = buildItems(res);
  } catch (e) {
    console.error("Failed to load local files", e);
  }
}

async function loadSettings() {
  try {
    const settings = await $fetch<{ value: string }>("/api/syncer/settings", {
      query: { value: "drive_path" },
    });
    drivePath.value = settings.value.replace(/\\/g, "/");
    currentPath.value = drivePath.value;
  } catch (e) {
    console.error("Failed to load settings", e);
  }
}

const websocket = useSyncerWebSocket();

onMounted(async () => {
  websocket.connect();

  await Promise.all([loadFiles(), loadSettings(), syncer.refresh()]);
});
</script>

<template>
  <UApp>
    <main
      class="h-screen w-full bg-default text-sm text-highlighted select-none"
    >
      <section class="flex h-full flex-col overflow-hidden">
        <!-- HEADER -->
        <header
          class="flex items-center justify-between border-b border-default px-3 py-2"
        >
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <UIcon
                :name="
                  syncer.enabled.value
                    ? 'material-symbols:cloud-sync-rounded'
                    : 'material-symbols:cloud-off-rounded'
                "
                class="size-5"
                :class="syncer.enabled.value ? 'text-primary' : 'text-muted'"
              />

              <h1 class="truncate text-sm font-semibold">NohamDrive Tray</h1>
            </div>

            <p class="truncate text-xs text-muted">
              {{
                syncer.enabled.value
                  ? `${syncedCount} synced items`
                  : "Synchronization paused"
              }}
            </p>
          </div>

          <div class="flex items-center gap-3">
            <UDropdownMenu :items="dropdownItems" variant="ghost" size="sm">
              <UButton
                :square="true"
                icon="material-symbols:more-vert"
                variant="ghost"
                size="sm"
                color="neutral"
              />
            </UDropdownMenu>
          </div>
        </header>

        <!-- PATH -->
        <div class="flex items-center gap-2 border-b border-default px-3 py-2">
          <UButton
            icon="material-symbols:arrow-upward-rounded"
            color="neutral"
            variant="soft"
            size="xs"
            aria-label="Parent folder"
            :disabled="!canGoUp || !syncer.enabled.value"
            @click="goUp"
          />

          <div
            class="min-w-0 flex-1 truncate rounded bg-muted px-2 py-1 font-mono text-[11px] text-muted"
          >
            <span
              v-for="(segment, index) in displayPathSegments"
              :key="`${segment}-${index}`"
            >
              <span v-if="index > 0" class="px-1 text-dimmed"> / </span>

              <span
                class="truncate"
                :class="segment === '…' ? 'text-dimmed' : ''"
              >
                {{ segment }}
              </span>
            </span>
          </div>
        </div>

        <!-- SEARCH -->
        <div
          class="grid grid-cols-[1fr_auto] gap-2 border-b border-default p-3"
        >
          <UInput
            v-model="search"
            icon="material-symbols:search-rounded"
            size="sm"
            placeholder="Search local files"
            :disabled="!syncer.enabled.value"
          />
        </div>

        <!-- CONTENT -->
        <div class="min-h-0 flex-1 overflow-y-auto">
          <!-- SYNC DISABLED -->
          <template v-if="!syncer.enabled.value">
            <div
              class="flex h-full flex-col items-center justify-center px-6 text-center"
            >
              <div
                class="mb-4 flex size-16 items-center justify-center rounded-full bg-muted"
              >
                <UIcon
                  name="material-symbols:cloud-off-rounded"
                  class="size-9 text-muted"
                />
              </div>

              <h2 class="text-sm font-semibold text-highlighted">
                Sync is paused
              </h2>

              <p class="mt-1 max-w-65 text-xs leading-relaxed text-muted">
                Your files are no longer synchronized
              </p>

              <div class="mt-5 flex items-center gap-2">
                <UButton
                  icon="material-symbols:play-arrow-rounded"
                  color="primary"
                  :loading="syncer.loading.value"
                  @click="syncer.start()"
                >
                  Resume Sync
                </UButton>

                <UButton
                  icon="material-symbols:refresh-rounded"
                  color="neutral"
                  variant="soft"
                  @click="syncer.refresh()"
                >
                  Refresh
                </UButton>
              </div>
            </div>
          </template>

          <!-- FILE EXPLORER -->
          <template v-else>
            <div class="flex flex-col">
              <div
                v-for="item in visibleItems"
                :key="item.id"
                class="group flex items-center gap-2 rounded-md px-3 py-2 transition-colors"
                :class="[
                  selectedId === item.id ? 'bg-primary/10' : 'hover:bg-muted',
                ]"
                @click="selectedId = item.id"
                @dblclick="openItem(item)"
              >
                <div class="shrink-0">
                  <UIcon
                    v-if="item.kind === 'folder'"
                    name="material-symbols:folder-rounded"
                    class="size-5 text-yellow-500"
                  />

                  <UIcon
                    v-else
                    name="material-symbols:description-rounded"
                    class="size-5 text-muted"
                  />
                </div>

                <div class="min-w-0 flex-1">
                  <p
                    class="truncate text-sm"
                    :class="[
                      selectedId === item.id
                        ? 'text-highlighted font-medium'
                        : 'text-toned',
                    ]"
                  >
                    {{ item.name }}
                  </p>

                  <p class="truncate text-xs text-muted">
                    {{ item.kind === "folder" ? "Folder" : "File" }}
                  </p>
                </div>

                <!-- ACTIONS -->
                <div
                  class="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100"
                >
                  <UButton
                    icon="material-symbols:more-horiz"
                    color="neutral"
                    variant="ghost"
                    size="xs"
                  />
                </div>
              </div>
            </div>

            <!-- EMPTY -->
            <div
              v-if="visibleItems.length === 0"
              class="flex h-full min-h-40 flex-col items-center justify-center gap-2 px-4 text-center text-muted"
            >
              <UIcon
                name="material-symbols:folder-off-rounded"
                class="size-8"
              />

              <p class="text-sm font-medium">Empty folder</p>
            </div>
          </template>
        </div>

        <!-- FOOTER -->
        <footer class="border-t border-default p-3">
          <div class="flex items-center justify-between gap-2">
            <div class="min-w-0">
              <p class="truncate text-xs font-medium">
                {{ selectedItem?.name || "No selection" }}
              </p>

              <p class="truncate text-[11px] text-muted">
                {{
                  selectedItem
                    ? selectedItem.kind === "folder"
                      ? "Folder"
                      : "File"
                    : "Select an item"
                }}
              </p>
            </div>

            <div
              class="flex items-center gap-1 rounded-full px-2 py-1 text-[10px] font-medium"
              :class="
                syncer.enabled
                  ? 'bg-primary/10 text-primary'
                  : 'bg-muted text-muted'
              "
            >
              <div
                class="size-1.5 rounded-full"
                :class="syncer.enabled.value ? 'bg-primary' : 'bg-muted'"
              />

              {{ syncer.enabled.value ? "SYNCING" : "PAUSED" }}
            </div>
          </div>
        </footer>
      </section>
    </main>
  </UApp>
</template>
