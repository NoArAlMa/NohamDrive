<script lang="ts" setup>
import type { AuthFormField, FormSubmitEvent } from "@nuxt/ui";
import * as z from "zod";

const props = defineProps<{
  mode: "login" | "register";
}>();

const mode = computed({
  get: () => props.mode,
  set: (value) => emit("update:mode", value),
});

const emit = defineEmits<{
  (e: "update:mode", value: "login" | "register"): void;
}>();

const loginFields: AuthFormField[] = [
  {
    name: "email",
    type: "email",
    label: "Email",
    placeholder: "Enter your email",
    required: true,
  },
  {
    name: "password",
    type: "password",
    label: "Password",
    placeholder: "Enter your password",
    required: true,
  },
  {
    name: "remember",
    label: "Remember me",
    type: "checkbox",
  },
];

const registerFields: AuthFormField[] = [
  {
    name: "username",
    type: "text",
    label: "Username",
    placeholder: "Enter a username",
    required: true,
  },
  {
    name: "email",
    type: "email",
    label: "Email",
    placeholder: "Enter your email",
    required: true,
  },
  {
    name: "password",
    type: "password",
    label: "Password",
    placeholder: "Choose a password",
    required: true,
  },
  {
    name: "password_confirmation",
    type: "password",
    label: "Confirm password",
    placeholder: "Confirm your password",
    required: true,
  },
];

const fields = computed(() =>
  mode.value === "login" ? loginFields : registerFields,
);

const loginSchema = z.object({
  email: z.email("Invalid email"),
  password: z
    .string("Password is required")
    .min(8, "Must be at least 8 characters"),
});

const createSchema = z
  .object({
    username: z
      .string("Username required")
      .min(3, "Must be at least 3 characters"),
    email: z.email("Invalid email"),
    password: z
      .string("Password is required")
      .min(8, "Must be at least 8 characters"),
    password_confirmation: z
      .string("Please confirm your password")
      .min(8, "Must be at least 8 characters"),
  })
  .refine((data) => data.password === data.password_confirmation, {
    message: "Passwords do not match",
    path: ["password_confirmation"],
  });

function onSubmit(payload: FormSubmitEvent<any>) {
  if (mode.value === "login") {
    console.log("LOGIN", payload.data);
  } else {
    console.log("REGISTER", payload.data);
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 p-4">
    <UPageCard class="w-full max-w-md">
      <Transition name="auth" mode="out-in">
        <UAuthForm
          :key="mode"
          :title="mode === 'login' ? 'Login' : 'Create account'"
          :schema="mode === 'login' ? loginSchema : createSchema"
          :description="
            mode === 'login'
              ? 'Enter your credentials to access your account.'
              : 'Create an account to get started.'
          "
          icon="i-lucide-user"
          :fields="fields"
          @submit="onSubmit"
          :submit="{
            label: mode === 'login' ? 'Login' : 'Create account',
            color: 'primary',
          }"
        >
          <template #footer>
            <UButton
              :label="
                mode === 'login'
                  ? 'Créer un compte'
                  : 'Déjà un compte ? Se connecter'
              "
              variant="link"
              color="secondary"
              @click="mode = mode === 'login' ? 'register' : 'login'"
              class="hover:cursor-pointer"
            />
          </template>
        </UAuthForm>
      </Transition>
    </UPageCard>
  </div>
</template>

<style scoped>
.auth-enter-active,
.auth-leave-active {
  transition: all 0.25s ease;
}

.auth-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.auth-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
