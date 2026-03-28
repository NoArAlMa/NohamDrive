<script lang="ts" setup>
const route = useRoute();
const router = useRouter();

definePageMeta({
  layout: false,
  middleware: "auth-middleware",
  invertAuth: true,
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

// On initialise le mode avec le query param ou 'login' par défaut
const mode = ref<"login" | "register">(
  route.query.mode === "register" ? "register" : "login",
);

// Watch pour mettre à jour si le query change
watch(
  () => route.query.mode,
  (newMode) => {
    mode.value = newMode === "register" ? "register" : "login";
  },
);
</script>

<template>
  <UApp class="relative overflow-hidden">
    <!-- Background animé -->
    <div
      class="gradient absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
    ></div>

    <UButton
      icon="material-symbols:arrow-back-rounded"
      color="neutral"
      variant="ghost"
      class="absolute left-3 top-3 z-1000"
      @click="navigateTo('/')"
      loading-auto
    />
    <section
      class="min-h-screen flex justify-center items-center gap-4 relative z-10"
    >
      <AuthForm v-model:mode="mode" class="grow" />
    </section>
  </UApp>
</template>

<style>
.gradient {
  --size: 750px;
  --speed: 50s;
  --easing: cubic-bezier(0.8, 0.2, 0.2, 0.8);

  width: var(--size);
  height: var(--size);
  filter: blur(calc(var(--size) / 5));
  background-image: linear-gradient(
    135deg,
    hsl(222, 84%, 60%),
    hsl(164, 79%, 71%)
  );
  animation: rotate var(--speed) var(--easing) alternate infinite;
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  z-index: -1;
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (min-width: 720px) {
  .gradient {
    --size: 500px;
  }
}
</style>
