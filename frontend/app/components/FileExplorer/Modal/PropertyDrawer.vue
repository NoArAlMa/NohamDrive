<script setup lang="ts">
import formatDate from "~/utils/date";
import type { ApiFileItem } from "~~/shared/types/file_tree";
import { useClipboard } from "@vueuse/core";

const { file, metadata } = defineProps<{
  file: ApiFileItem;
  metadata: FileMetadata;
}>();

const action = useFsActions();

const filePath = ref(metadata.path);
const { copy, copied } = useClipboard({ source: filePath });

const confirmModal = ref(false);

const emit = defineEmits<{ close: [boolean] }>();
</script>

<template>
  <USlideover>
    <template #header>
      <section class="w-full flex flex-row items-center justify-between">
        <div class="w-full truncate flex items-center">
          <UIcon
            :name="
              file.is_dir ? 'explorer:folder-icon' : getFileIcon(file.name)
            "
            class="size-5 mr-2"
          />
          <span class="font-semibold">{{ metadata.name }}</span>
        </div>
        <div>
          <UButton
            icon="material-symbols:close-rounded"
            variant="ghost"
            color="neutral"
            @click="emit('close', false)"
          />
        </div>
      </section>
    </template>
    <template #body>
      <!-- TYPE GLOBAL -->
      <section
        class="flex flex-col gap-2 [&>div>h3]:font-semibold [&>div>span]:text-muted [&>div]:flex [&>div]:justify-between [&>div]:items-center"
      >
        <div class="relative group flex items-center gap-2">
          <h3 class="mr-auto">Path :</h3>
          <div class="opacity-0 group-hover:opacity-100 transition">
            <UTooltip text="Copy path" :delay-duration="10">
              <UButton
                :icon="
                  copied
                    ? 'material-symbols:check-small-rounded'
                    : 'material-symbols:content-copy-outline-rounded'
                "
                size="sm"
                variant="ghost"
                :color="copied ? 'success' : 'neutral'"
                @click="copy()"
              />
            </UTooltip>
          </div>

          <span :title="metadata.path" class="text-muted truncate max-w-[70%]">
            {{ metadata.path }}
          </span>
        </div>

        <div>
          <h3>Last modified :</h3>
          <span>{{ formatDate(metadata.last_modified!) }}</span>
        </div>
        <div v-if="!file.is_dir">
          <h3>Type :</h3>
          <span>{{ metadata.content_type }}</span>
        </div>

        <div>
          <h3>Size :</h3>
          <span>{{ formatFileSize(metadata.size_bytes, 1) }}</span>
        </div>
        <div v-if="file.is_dir">
          <h3>Number of files :</h3>
          <span>{{ metadata.file_count! }}</span>
        </div>
      </section>
      <div v-if="['video', 'image', 'audio'].includes(metadata.content_type)">
        <USeparator class="my-6" :decorative="true" orientation="horizontal" />

        <section
          class="flex flex-col gap-2 [&>div>div>h3]:font-semibold [&>div>div>span]:text-muted [&>div>div]:flex [&>div>div]:justify-between [&>div>div]:items-center"
        >
          <div
            class="flex flex-col gap-2"
            v-if="metadata.content_type === 'image'"
          >
            <div>
              <h3>Width :</h3>
              <span>{{ metadata.width }}px</span>
            </div>
            <div>
              <h3>Height :</h3>
              <span>{{ metadata.height }}px</span>
            </div>
            <div>
              <h3>Format :</h3>
              <span>{{ metadata.format }}</span>
            </div>
          </div>

          <div
            class="flex flex-col gap-2"
            v-if="metadata.content_type === 'video'"
          >
            <div>
              <h3>Width :</h3>
              <span>{{ metadata.width }}px</span>
            </div>
            <div>
              <h3>Height :</h3>
              <span>{{ metadata.height }}px</span>
            </div>
            <div>
              <h3>Duration :</h3>
              <span>{{ formatDuration(metadata.duration!) }}</span>
            </div>
            <div>
              <h3>Codec :</h3>
              <span>{{ metadata.codec! }}</span>
            </div>
            <div>
              <h3>Framerate :</h3>
              <span>{{ metadata.fps }} FPS</span>
            </div>
          </div>
        </section>
      </div>
    </template>
    <template #footer>
      <section class="w-full flex flex-col gap-2">
        <UButton
          :icon="
            file.is_dir
              ? 'material-symbols:folder-open-rounded'
              : 'material-symbols:visibility-outline-rounded'
          "
          :label="`Open the ${file.is_dir ? 'folder' : 'file'}`"
          variant="subtle"
          @click="
            action.open(file);
            emit('close', false);
          "
        />
        <UModal
          title="Confirm"
          :description="`Do you really want to delete ${metadata.name} ?`"
          v-model:open="confirmModal"
        >
          <UButton
            label="Delete"
            color="error"
            variant="soft"
            icon="material-symbols:delete-outline-rounded"
          />
          <template #footer="{ close }">
            <div class="w-full flex gap-2 justify-end items-center">
              <UButton
                label="Cancel"
                color="error"
                variant="outline"
                @click="close()"
              />
              <UButton
                label="Confirm"
                color="primary"
                variant="soft"
                @click="
                  action.del(file);
                  close();
                  emit('close', false);
                "
              />
            </div>
          </template>
        </UModal>
      </section>
    </template>
  </USlideover>
</template>
