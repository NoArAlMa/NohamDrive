<script lang="ts" setup>
definePageMeta({
  middleware: "prod-middleware",
});
</script>

<template>
  <UApp class="h-screen w-screen">
    <AuthForm />
  </UApp>
</template>
