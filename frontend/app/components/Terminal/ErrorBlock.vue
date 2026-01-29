<script lang="ts" setup>
const props = defineProps<{
  content: string;
}>();
</script>

<template>
  <div>
    <span class="text-red-600 whitespace-nowrap">
      {{ props.content }}
    </span>
  </div>
</template>
