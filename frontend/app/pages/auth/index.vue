<script lang="ts" setup>
const route = useRoute();
const router = useRouter();

definePageMeta({
  layout: false,
});

useHead({
  title: "Login & Register - NohamDrive",
  meta: [
    {
      name: "NohamDrive | Authentication",
      content: "Connect yourself to your next favorite app",
    },
  ],
});

const mode = ref<"login" | "register">("login");
</script>
²
<template>
  <section class="min-h-screen flex justify-center items-center">
    <AuthForm v-model:mode="mode" class="grow" />
  </section>
</template>
