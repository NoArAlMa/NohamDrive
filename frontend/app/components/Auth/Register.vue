<script lang="ts" setup>
import type { AuthFormField, FormSubmitEvent, StepperItem } from "@nuxt/ui";
import * as z from "zod";

const { t } = useI18n();

const authForm = useTemplateRef("authForm");
const generalError = ref<string | null>(null);
const step = ref(0);

const items = computed<StepperItem[]>(() => [
  {
    title: t("auth.fullName") as string,
    icon: "material-symbols:person-outline-rounded",
  },
  {
    title: t("auth.password") as string,
    icon: "material-symbols:lock-outline",
  },
]);

const steps = [
  {
    id: 0,
    title: "Account",
    fields: ["name", "username", "email"],
  },
  {
    id: 1,
    title: "Security",
    fields: ["password", "password_confirmation"],
  },
];

const isLastStep = computed(() => step.value === steps.length - 1);

const registerFields = computed<AuthFormField[]>(() => [
  {
    name: "name",
    type: "text",
    label: t("auth.fullName") as string,
    placeholder: t("auth.placeholders.enterName") as string,
    required: true,
  },
  {
    name: "username",
    type: "text",
    label: t("auth.username") as string,
    placeholder: t("auth.placeholders.enterUsername") as string,
    required: true,
  },
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
    placeholder: t("auth.placeholders.choosePassword") as string,
    required: true,
  },
  {
    name: "password_confirmation",
    type: "password",
    label: t("auth.confirmPassword") as string,
    placeholder: t("auth.placeholders.confirmPassword") as string,
    required: true,
  },
]);

const currentFields = computed(() => {
  return registerFields.value.filter((field) =>
    steps[step.value]!.fields.includes(field.name),
  );
});

const stepSchemas = [
  z.object({
    name: z
      .string(t("auth.validation.fullNameRequired") as string)
      .min(3, t("auth.validation.min3") as string),
    username: z
      .string(t("auth.validation.usernameRequired") as string)
      .min(3, t("auth.validation.min3") as string),
    email: z.email(t("auth.validation.invalidEmail") as string),
  }),
  z
    .object({
      password: z
        .string(t("auth.validation.passwordRequired") as string)
        .min(8, t("auth.validation.min8") as string),
      password_confirmation: z
        .string(t("auth.validation.confirmPasswordRequired") as string)
        .min(8, t("auth.validation.min8") as string),
    })
    .refine((data) => data.password === data.password_confirmation, {
      message: t("auth.validation.passwordsDontMatch") as string,
      path: ["password_confirmation"],
    }),
];

const step1Fields = ["name", "username", "email"];
const hasStep1Errors = ref(false);

const fullData = reactive<any>({});

const { registerUser } = useAuth();

function buildGeneralError(
  errors: { name?: string; message: string }[],
): string | null {
  const fieldsInError = errors
    .map((err) => err.name)
    .filter((name): name is string => !!name && step1Fields.includes(name));

  if (fieldsInError.length === 0) return null;

  const uniqueFields = [...new Set(fieldsInError)];

  return `Error on ${uniqueFields.join(", ")}`;
}

async function onSubmit() {
  generalError.value = null;
  hasStep1Errors.value = false;

  const result = await registerUser(fullData);
  if (!result) return;

  if (result.statusCode === 422) {
    hasStep1Errors.value = true;
    generalError.value =
      result.message || buildGeneralError(result.fieldErrors || []);
  }

  if (result.fieldErrors?.length) {
    hasStep1Errors.value = true;

    generalError.value = buildGeneralError(result.fieldErrors);
    authForm.value?.formRef?.setErrors(result.fieldErrors);
  }

  if (result.success) {
    await navigateTo("/home");
  }

  return result;
}
async function handleNext(payload: FormSubmitEvent<any>): Promise<void> {
  Object.assign(fullData, payload.data);

  await stepSchemas[step.value]!.parseAsync(payload.data);

  hasStep1Errors.value = false;

  if (!isLastStep.value) {
    step.value++;
    return;
  }

  await onSubmit();
}
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 p-4">
    <UPageCard class="w-full max-w-md shadow-md">
      <UStepper
        v-model="step"
        :items="items"
        :disabled="true"
        class="w-full"
        size="sm"
      />

      <UAuthForm
        ref="authForm"
        :title="String(t('auth.createAccount'))"
        :schema="stepSchemas[step]"
        :fields="currentFields"
        @submit="handleNext"
        loading-auto
        :submit="{
          label: isLastStep
            ? (t('auth.createAccount') as string)
            : (t('auth.next') as string),
          color: 'primary',
        }"
      >
        <template #description>
          {{ t("auth.haveAccount") }}
          <ULink
            @click="$emit('switch-mode', 'login')"
            class="text-primary font-medium"
            >{{ t("auth.logIn") }}</ULink
          >.
        </template>
        <template #validation>
          <UAlert
            v-if="generalError"
            color="error"
            variant="subtle"
            icon="material-symbols:info-outline-rounded"
            :title="generalError"
          />
        </template>

        <template #footer>
          <div class="flex w-full">
            <UButton
              v-if="step > 0"
              :label="String(t('auth.back'))"
              @click="step--"
              variant="ghost"
              icon="material-symbols:arrow-back-rounded"
            >
              <template #trailing>
                <UIcon
                  v-if="hasStep1Errors"
                  name="material-symbols:info-outline-rounded"
                  class="text-error"
                />
              </template>
            </UButton>
          </div>
        </template>
      </UAuthForm>
    </UPageCard>
  </div>
</template>
