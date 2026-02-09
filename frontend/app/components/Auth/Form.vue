<script lang="ts" setup>
import type { AuthFormField, FormSubmitEvent } from "@nuxt/ui";
// import * as z from "zod";

const mode = ref<"login" | "register">("login");

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

function onSubmit(payload: FormSubmitEvent<any>) {
  if (mode.value === "login") {
    console.log("LOGIN", payload);
  } else {
    console.log("REGISTER", payload);
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 p-4">
    <UPageCard class="w-full max-w-md">
      <UAuthForm
        :title="mode === 'login' ? 'Login' : 'Créer un compte'"
        :description="
          mode === 'login'
            ? 'Enter your credentials to access your account.'
            : 'Create an account to get started.'
        "
        icon="i-lucide-user"
        :fields="fields"
        @submit="onSubmit"
        :submit="{
          label: mode === 'login' ? 'Se connecter' : 'Créer un compte',
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
          />
        </template>
      </UAuthForm>
    </UPageCard>
  </div>
</template>
