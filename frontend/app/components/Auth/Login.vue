<script lang="ts" setup>
import type { AuthFormField, FormSubmitEvent } from "@nuxt/ui";
import * as z from "zod";

const { t } = useI18n();

const authForm = useTemplateRef("authForm");
const { loginUser } = useAuth();

const generalError = ref<string | null>(null);

const loginFields = computed<AuthFormField[]>(() => [
  {
    name: "email",
    type: "email",
    label: t("auth.email") as string,
    placeholder: t("auth.placeholders.enterEmail") as string,
    required: true,
  },
  {
    name: "password",
    type: "password",
    label: t("auth.password") as string,
    placeholder: t("auth.placeholders.enterPassword") as string,
    required: true,
  },
  {
    name: "remember",
    label: t("auth.rememberMe") as string,
    type: "checkbox",
  },
]);

const loginSchema = z.object({
  email: z.email(t("auth.validation.invalidEmail") as string),
  password: z
    .string(t("auth.validation.passwordRequired") as string)
    .min(8, t("auth.validation.min8") as string),
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
        :title="String(t('auth.login'))"
        :schema="loginSchema"
        icon="i-lucide-user"
        :fields="loginFields"
        @submit="onSubmit"
        loading-auto
        :submit="{
          label: String(t('auth.login')),
          color: 'primary',
        }"
      >
        <template #description>
          {{ t("auth.noAccount") }}
          <ULink
            @click="$emit('switch-mode', 'register')"
            class="text-primary font-medium"
            >{{ t("auth.signUp") }}</ULink
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
          <ULink class="text-primary" to="/">{{
            t("auth.forgotPassword")
          }}</ULink>
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
