<script lang="ts" setup>
type LocalItem = {
  id: number;
  name: string;
  kind: "folder" | "file";
  parent: string;
  size: string;
  modified: string;
  synced: boolean;
};

definePageMeta({
  layout: false,
  middleware: "electron-middleware",
});

const currentPath = ref("C:/Users/Alex/NohamDrive");
const selectedId = ref<number | null>(1);
const search = ref("");
const newFolderName = ref("");
const renamingId = ref<number | null>(null);
const renameValue = ref("");

const localItems = ref<LocalItem[]>([
  {
    id: 1,
    name: "Documents",
    kind: "folder",
    parent: "C:/Users/Alex/NohamDrive",
    size: "12 items",
    modified: "Today, 09:42",
    synced: true,
  },
  {
    id: 2,
    name: "Screenshots",
    kind: "folder",
    parent: "C:/Users/Alex/NohamDrive",
    size: "48 items",
    modified: "Yesterday",
    synced: false,
  },
  {
    id: 3,
    name: "Roadmap.pdf",
    kind: "file",
    parent: "C:/Users/Alex/NohamDrive",
    size: "2.4 MB",
    modified: "Today, 08:10",
    synced: true,
  },
  {
    id: 4,
    name: "Brand-assets.zip",
    kind: "file",
    parent: "C:/Users/Alex/NohamDrive",
    size: "18.7 MB",
    modified: "Mon",
    synced: false,
  },
  {
    id: 5,
    name: "Invoices",
    kind: "folder",
    parent: "C:/Users/Alex/NohamDrive/Documents",
    size: "9 items",
    modified: "Apr 24",
    synced: true,
  },
  {
    id: 6,
    name: "Contract.docx",
    kind: "file",
    parent: "C:/Users/Alex/NohamDrive/Documents",
    size: "186 KB",
    modified: "Apr 23",
    synced: true,
  },
]);

const visibleItems = computed(() => {
  const query = search.value.trim().toLowerCase();
  return localItems.value
    .filter((item) => item.parent === currentPath.value)
    .filter((item) => !query || item.name.toLowerCase().includes(query))
    .sort((a, b) => {
      if (a.kind !== b.kind) return a.kind === "folder" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
});

const selectedItem = computed(
  () => localItems.value.find((item) => item.id === selectedId.value) ?? null,
);

const pathSegments = computed(() => currentPath.value.split("/"));
const canGoUp = computed(
  () => currentPath.value !== "C:/Users/Alex/NohamDrive",
);
const syncedCount = computed(
  () => localItems.value.filter((item) => item.synced).length,
);

function iconFor(item: LocalItem) {
  if (item.kind === "folder") return "material-symbols:folder-rounded";
  if (item.name.endsWith(".pdf"))
    return "material-symbols:picture-as-pdf-rounded";
  if (item.name.endsWith(".zip")) return "material-symbols:folder-zip-rounded";
  return "material-symbols:description-rounded";
}

function openItem(item: LocalItem) {
  selectedId.value = item.id;
  if (item.kind === "folder") {
    currentPath.value = `${item.parent}/${item.name}`;
    selectedId.value = null;
    search.value = "";
  }
}

function goUp() {
  if (!canGoUp.value) return;
  currentPath.value = currentPath.value.split("/").slice(0, -1).join("/");
  selectedId.value = null;
}

function createFolder() {
  const name = newFolderName.value.trim();
  if (!name) return;

  localItems.value.push({
    id: Date.now(),
    name,
    kind: "folder",
    parent: currentPath.value,
    size: "0 items",
    modified: "Just now",
    synced: false,
  });
  newFolderName.value = "";
}

function startRename() {
  if (!selectedItem.value) return;
  renamingId.value = selectedItem.value.id;
  renameValue.value = selectedItem.value.name;
}

function submitRename() {
  const item = selectedItem.value;
  const name = renameValue.value.trim();
  if (!item || !name) return;

  item.name = name;
  item.modified = "Just now";
  item.synced = false;
  renamingId.value = null;
}

function deleteSelected() {
  if (!selectedItem.value) return;

  const item = selectedItem.value;
  const itemPath = `${item.parent}/${item.name}`;
  localItems.value = localItems.value.filter(
    (candidate) =>
      candidate.id !== item.id && !candidate.parent.startsWith(`${itemPath}/`),
  );
  selectedId.value = null;
}

function toggleSync(item = selectedItem.value) {
  if (!item) return;
  item.synced = !item.synced;
  item.modified = "Just now";
}
</script>

<template>
  <UApp>
    <main
      class="h-screen w-full bg-default text-sm text-highlighted select-none"
    >
      <section class="flex h-full flex-col overflow-hidden">
        <header
          class="flex items-center justify-between border-b border-default px-3 py-2"
        >
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <UIcon
                name="material-symbols:cloud-sync-rounded"
                class="size-5 text-primary"
              />
              <h1 class="truncate text-sm font-semibold">NohamDrive Tray</h1>
            </div>
            <p class="truncate text-xs text-muted">
              {{ syncedCount }} synced items on this device
            </p>
          </div>

          <div class="flex items-center gap-1">
            <UButton
              icon="material-symbols:refresh-rounded"
              color="neutral"
              variant="ghost"
              size="xs"
              aria-label="Refresh"
            />
            <UButton
              icon="material-symbols:settings-rounded"
              color="neutral"
              variant="ghost"
              size="xs"
              aria-label="Settings"
            />
          </div>
        </header>

        <div class="flex items-center gap-2 border-b border-default px-3 py-2">
          <UButton
            icon="material-symbols:arrow-upward-rounded"
            color="neutral"
            variant="soft"
            size="xs"
            :disabled="!canGoUp"
            aria-label="Parent folder"
            @click="goUp"
          />
          <div
            class="min-w-0 flex-1 truncate rounded bg-muted px-2 py-1 font-mono text-[11px] text-muted"
          >
            <span
              v-for="(segment, index) in pathSegments"
              :key="`${segment}-${index}`"
            >
              <span v-if="index > 0" class="px-0.5 text-dimmed">/</span>
              {{ segment }}
            </span>
          </div>
        </div>

        <div
          class="grid grid-cols-[1fr_auto] gap-2 border-b border-default p-3"
        >
          <UInput
            v-model="search"
            icon="material-symbols:search-rounded"
            size="sm"
            placeholder="Search local files"
          />
          <UButton
            icon="material-symbols:folder-open-rounded"
            color="primary"
            variant="soft"
            size="sm"
            aria-label="Choose folder"
          />
        </div>

        <div class="flex items-center gap-2 border-b border-default px-3 py-2">
          <UInput
            v-model="newFolderName"
            size="xs"
            placeholder="New folder"
            class="min-w-0 flex-1"
            @keydown.enter.prevent="createFolder"
          />
          <UButton
            icon="material-symbols:create-new-folder-rounded"
            color="neutral"
            variant="soft"
            size="xs"
            aria-label="Create folder"
            @click="createFolder"
          />
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto">
          <button
            v-for="item in visibleItems"
            :key="item.id"
            type="button"
            class="grid w-full grid-cols-[auto_1fr_auto] items-center gap-2 border-b border-muted px-3 py-2 text-left transition-colors hover:bg-muted"
            :class="{ 'bg-primary/10': selectedId === item.id }"
            @click="selectedId = item.id"
            @dblclick="openItem(item)"
          >
            <UIcon
              :name="iconFor(item)"
              class="size-5"
              :class="item.kind === 'folder' ? 'text-primary' : 'text-muted'"
            />

            <div class="min-w-0">
              <UInput
                v-if="renamingId === item.id"
                v-model="renameValue"
                size="xs"
                autofocus
                @click.stop
                @keydown.enter.prevent="submitRename"
                @keydown.esc="renamingId = null"
                @blur="submitRename"
              />
              <p v-else class="truncate font-medium">{{ item.name }}</p>
              <p class="truncate text-xs text-muted">
                {{ item.size }} - {{ item.modified }}
              </p>
            </div>

            <UButton
              :icon="
                item.synced
                  ? 'material-symbols:check-circle-rounded'
                  : 'material-symbols:sync-problem-rounded'
              "
              :color="item.synced ? 'success' : 'warning'"
              variant="ghost"
              size="xs"
              :aria-label="item.synced ? 'Synced' : 'Needs sync'"
              @click.stop="toggleSync(item)"
            />
          </button>

          <div
            v-if="visibleItems.length === 0"
            class="flex h-full min-h-40 flex-col items-center justify-center gap-2 px-4 text-center text-muted"
          >
            <UIcon name="material-symbols:folder-off-rounded" class="size-8" />
            <p class="text-sm font-medium">No local item found</p>
          </div>
        </div>

        <footer class="border-t border-default p-3">
          <div
            v-if="selectedItem"
            class="flex items-center justify-between gap-2"
          >
            <div class="min-w-0">
              <p class="truncate text-xs font-medium">
                {{ selectedItem.name }}
              </p>
              <p class="truncate text-[11px] text-muted">
                {{
                  selectedItem.synced
                    ? "Available in cloud"
                    : "Local changes pending"
                }}
              </p>
            </div>

            <div class="flex items-center gap-1">
              <UButton
                icon="material-symbols:drive-file-move-rounded"
                color="neutral"
                variant="soft"
                size="xs"
                aria-label="Move"
              />
              <UButton
                icon="material-symbols:edit-rounded"
                color="neutral"
                variant="soft"
                size="xs"
                aria-label="Rename"
                @click="startRename"
              />
              <UButton
                icon="material-symbols:delete-outline-rounded"
                color="error"
                variant="soft"
                size="xs"
                aria-label="Delete"
                @click="deleteSelected"
              />
            </div>
          </div>

          <div v-else class="flex items-center justify-between gap-2">
            <p class="text-xs text-muted">Select an item to manage it</p>
            <UButton
              icon="material-symbols:cloud-upload-rounded"
              label="Sync all"
              color="primary"
              size="xs"
            />
          </div>
        </footer>
      </section>
    </main>
  </UApp>
</template>
