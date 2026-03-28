<script lang="ts" setup>
import type { AuthFormField, FormSubmitEvent } from "@nuxt/ui";
import * as z from "zod";

const authForm = useTemplateRef("authForm");
const { loginUser } = useAuth();

const generalError = ref<string | null>(null);

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

const loginSchema = z.object({
  email: z.email("Invalid email"),
  password: z
    .string("Password is required")
    .min(8, "Must be at least 8 characters"),
});

async function onSubmit(payload: FormSubmitEvent<any>) {
  generalError.value = null;

  const result = await loginUser(payload.data);

  if (result?.fieldErrors) {
    authForm.value?.formRef?.setErrors(result.fieldErrors);
  }
  if (result?.statusCode === 422 && result?.message) {
    generalError.value = result.message;
    return;
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 p-4">
    <UPageCard class="w-full max-w-md shadow-md">
      <UAuthForm
        ref="authForm"
        title="Login"
        :schema="loginSchema"
        icon="i-lucide-user"
        :fields="loginFields"
        @submit="onSubmit"
        loading-auto
        :submit="{
          label: 'Login',
          color: 'primary',
        }"
      >
        <template #description>
          Don't have an account?
          <ULink
            @click="$emit('switch-mode', 'register')"
            class="text-primary font-medium"
            >Sign up</ULink
          >
        </template>
        <template #validation>
          <UAlert
            v-if="generalError"
            color="error"
            variant="subtle"
            icon="i-lucide-info"
            :title="generalError"
          />
        </template>
        <template #password-hint>
          <ULink class="text-primary" to="/">Forgot your password ?</ULink>
        </template>
      </UAuthForm>
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
