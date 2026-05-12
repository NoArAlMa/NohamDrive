<script lang="ts" setup>
import { Cropper, CircleStencil } from "vue-advanced-cropper";
import "vue-advanced-cropper/dist/style.css";

import type { GenericAPIResponse } from "~~/shared/types/API";

const open = defineModel<boolean>("open", { default: false });

const emit = defineEmits<{
  (e: "updated"): void;
}>();

const toast = useToast();

const originalFile = ref<File | null>(null);
const imageUrl = ref<string | null>(null);

const cropper = ref<any>(null);

const uploading = ref(false);
const errorMessage = ref<string | null>(null);

function onFileSelected(file: File | null | undefined) {
  errorMessage.value = null;

  if (!file) return;

  // Vérification taille max 5MB
  if (file.size > 5 * 1024 * 1024) {
    errorMessage.value = "Image must be smaller than 5MB.";
    return;
  }

  // Nettoyage ancienne preview
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value);
  }

  originalFile.value = file;
  imageUrl.value = URL.createObjectURL(file);
}

async function generateCroppedImage(): Promise<Blob | null> {
  const result = cropper.value?.getResult({
    width: 512,
    height: 512,
  });

  const canvas = result?.canvas;

  if (!canvas) {
    return null;
  }

  return new Promise((resolve) => {
    canvas.toBlob(
      (blob: Blob) => {
        resolve(blob);
      },
      "image/png",
      0.95,
    );
  });
}

async function upload() {
  errorMessage.value = null;

  if (!imageUrl.value) {
    errorMessage.value = "Please select an image.";
    return;
  }

  uploading.value = true;

  try {
    const blob = await generateCroppedImage();

    if (!blob) {
      errorMessage.value = "Unable to crop image.";
      return;
    }

    const form = new FormData();

    form.append("file", blob, "avatar.png");

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

    reset();

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

function reset() {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value);
  }

  originalFile.value = null;
  imageUrl.value = null;
  errorMessage.value = null;
}

watch(open, (value) => {
  if (!value) {
    reset();
  }
});

onBeforeUnmount(() => {
  reset();
});
</script>

<template>
  <UModal
    v-model:open="open"
    title="Profile picture"
    description="Upload and crop your new profile picture."
  >
    <template #body>
      <div class="space-y-4">
        <UFileUpload
          v-if="!imageUrl"
          accept="image/*"
          :multiple="false"
          :dropzone="true"
          label="Drop an image here"
          description="PNG, JPG, WEBP — Max 5MB"
          class="max-h-100"
          @update:model-value="onFileSelected"
        />

        <div
          v-if="imageUrl"
          class="overflow-hidden rounded-xl border border-default"
        >
          <Cropper
            ref="cropper"
            :src="imageUrl"
            :stencil-component="CircleStencil"
            :stencil-props="{
              aspectRatio: 1,
            }"
            image-restriction="stencil"
            class="h-96 w-full bg-elevated"
          />
        </div>

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
            :disabled="!imageUrl"
            @click="upload"
          >
            Upload
          </UButton>
        </div>
      </div>
    </template>
  </UModal>
</template>
