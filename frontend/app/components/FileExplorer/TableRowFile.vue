<script lang="ts" setup>
import type { TableRow } from "@nuxt/ui";

const props = defineProps<{
  row: TableRow<ApiFileItem>;
}>();

const action = useFsActions();

function onRowClick() {
  if (!props.row) return;
  try {
    props.row.toggleSelected?.();
  } catch (e) {
    console.log("lala");
  }
}
</script>

<template>
  <div
    class="relative h-full flex items-center group"
    @click="onRowClick"
    @dblclick="action.open(props.row.original)"
  >
    <!-- Icone dossier ou fichier -->
    <UIcon
      v-if="row.original.is_dir"
      name="heroicons-folder"
      class="text-lg mr-2"
    />
    <UIcon
      v-else
      :name="getFileIcon(row.original.name)"
      class="text-lg mr-2"
      :alt="`Icon for ${row.original.name}`"
    />

    <!-- Nom du fichier -->
    <ULink>
      <span
        class="hover:underline underline-offset-2 cursor-pointer"
        @click="action.open(props.row.original)"
      >
        {{ row.getValue("name") }}
      </span>
    </ULink>
  </div>
</template>
