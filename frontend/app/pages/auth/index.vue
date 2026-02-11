<script lang="ts" setup>
const route = useRoute();
const router = useRouter();

const mode = ref<"login" | "register">("login");
</script>
²
<template>
  <section class="min-h-screen flex justify-center items-center">
    <AuthForm v-model:mode="mode" class="grow" />
  </section>
</template>
