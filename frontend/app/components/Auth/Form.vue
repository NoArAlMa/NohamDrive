<script lang="ts" setup>
import { AuthLogin, AuthRegister } from "#components";

const route = useRoute();
const router = useRouter();

// Initial mode from query param
const mode = ref<"login" | "register">(
  route.query.mode === "register" ? "register" : "login",
);

// Function to switch mode and update query param
function switchMode(newMode: "login" | "register") {
  mode.value = newMode;
  router.replace({ query: { mode: newMode } });
}

// Optional computed for rendering
const currentForm = computed(() =>
  mode.value === "login" ? AuthLogin : AuthRegister,
);
</script>

<template>
  <div class="w-full max-w-md">
    <transition name="auth-slide" mode="out-in">
      <component :is="currentForm" :key="mode" @switch-mode="switchMode" />
    </transition>
  </div>
</template>

<style scoped>
.auth-slide-enter-active,
.auth-slide-leave-active {
  transition: all 0.3s ease;
}

.auth-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.auth-slide-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.auth-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.auth-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
