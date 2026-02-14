<script setup lang="ts">
import type { NuxtError } from "#app";

const props = defineProps<{
  error: NuxtError;
}>();
</script>

<template>
  <UError
    :error="error"
    :ui="{
      statusCode: 'text-5xl font-bold text-primary',
      statusMessage: 'text-2xl font-medium text-neutral',
    }"
  />
</template>
