<script lang="ts" setup>
const route = useRoute();
const router = useRouter();

const mode = computed<"login" | "register">({
  get() {
    return route.query.mode === "register" ? "register" : "login";
  },
  set(value) {
    router.replace({
      query: {
        ...route.query,
        mode: value === "login" ? undefined : "register",
      },
    });
  },
});
</script>

<template>
  <section class="min-h-screen flex justify-center items-center">
    <AuthForm v-model:mode="mode" class="grow" />
  </section>
</template>
