<script setup lang="ts">
import { useCookie } from "#app";

const path = ref("");
const loading = ref(false);
const saved = ref(false);

const token = useCookie("auth_token");
const { setAutoStart, autoStart } = useSyncState();

async function openFolderPicker() {
  loading.value = true;
  saved.value = false;

  try {
    const selected = await (window as any).electronAPI.selectFolder();
    if (!selected) return;

    path.value = selected;
  } finally {
    loading.value = false;
  }
}

async function saveSettings() {
  if (!path.value) return;

  loading.value = true;
  saved.value = false;

  try {
    await $fetch("/api/syncer/settings", {
      method: "PATCH",
      body: {
        drive_path: path.value,
        token: token.value,
      },
    });
    saved.value = true;
  } finally {
    loading.value = false;
    navigateTo("/home");
  }
}
</script>
<template>
  <UPageCard class="w-full max-w-md shadow-lg rounded-2xl">
    <div class="space-y-6 p-2">
      <!-- HEADER -->
      <div class="space-y-1">
        <h2 class="text-lg font-semibold">Sync settings</h2>
        <p class="text-sm text-gray-500">
          Choose where your files will be synchronized locally.
        </p>
      </div>

      <UForm class="space-y-5">
        <!-- PATH SELECTOR -->
        <UFormField
          label="Storage location"
          description="This folder will store synced files"
        >
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <UInput
                :model-value="path"
                class="flex-1"
                placeholder="No folder selected"
                icon="material-symbols:folder-outline-rounded"
                readonly
              />

              <UButton
                color="primary"
                variant="soft"
                icon="material-symbols:folder-open-rounded"
                :loading="loading"
                @click="openFolderPicker"
              >
                {{ path ? "Change" : "Browse" }}
              </UButton>
            </div>

            <!-- PATH PREVIEW -->
            <div v-if="path" class="text-xs text-gray-500 break-all">
              Selected:
              <span class="font-medium text-gray-700">{{ path }}</span>
            </div>
          </div>
        </UFormField>

        <UFormField
          label="Auto-sync"
          description="Keep files up to date automatically"
        >
          <USwitch
            :model-value="autoStart"
            @update:model-value="setAutoStart"
          />
        </UFormField>

        <!-- SUCCESS MESSAGE -->
        <div
          v-if="saved"
          class="text-green-500 text-sm flex items-center gap-1"
        >
          <span>✓</span>
          Settings saved successfully
        </div>

        <!-- ACTIONS -->
        <div class="flex justify-end pt-2">
          <UButton
            color="primary"
            size="md"
            :disabled="!path || loading"
            :loading="loading"
            @click="saveSettings"
          >
            Save settings
          </UButton>
        </div>
      </UForm>
    </div>
  </UPageCard>
</template>
