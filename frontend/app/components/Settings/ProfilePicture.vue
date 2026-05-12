<script lang="ts" setup>
import type { GenericAPIResponse } from "~~/shared/types/API";

const open = defineModel<boolean>("open", { default: false });
const emit = defineEmits<{
  (e: "updated"): void;
}>();

const file = ref<File | null>(null);
const uploading = ref(false);
const errorMessage = ref<string | null>(null);

const toast = useToast();

async function upload() {
  errorMessage.value = null;

  if (!file.value) {
    errorMessage.value = "Please select a file.";
    return;
  }

  uploading.value = true;
  try {
    const form = new FormData();
    form.append("file", file.value);

    await $fetch<GenericAPIResponse<Record<string, any>>>(
      "/api/users/me/profile-picture",
      {
        method: "POST",
        body: form,
      },
    );

    toast.add({
      title: "Profile picture updated",
      color: "success",
      icon: "material-symbols:check-rounded",
    });

    emit("updated");
    file.value = null;
    open.value = false;
  } catch (error: any) {
    errorMessage.value =
      error?.data?.message ||
      error?.response?._data?.message ||
      "Unable to upload profile picture";
  } finally {
    uploading.value = false;
  }
}
</script>

<template>
  <UModal
    v-model:open="open"
    title="Profile picture"
    description="Upload a new profile picture (PNG/JPG/SVG)."
  >
    <template #body>
      <div class="space-y-4">
        <UFileUpload
          v-model="file"
          accept="image/*,image/svg+xml"
          :multiple="false"
          :dropzone="true"
          label="Drop an image here"
          description="Max 5MB"
          class="max-h-100"
        />

        <p v-if="errorMessage" class="text-sm text-error">
          {{ errorMessage }}
        </p>

        <div class="flex justify-end gap-2">
          <UButton
            color="neutral"
            variant="ghost"
            :disabled="uploading"
            @click="open = false"
          >
            Cancel
          </UButton>
          <UButton
            color="primary"
            variant="subtle"
            icon="material-symbols:upload-rounded"
            :loading="uploading"
            :disabled="!file"
            @click="upload"
          >
            Upload
          </UButton>
        </div>
      </div>
    </template>
  </UModal>
</template>
