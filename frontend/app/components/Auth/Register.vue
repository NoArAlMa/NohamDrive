<script lang="ts" setup>
import type { AuthFormField, FormSubmitEvent, StepperItem } from "@nuxt/ui";
import * as z from "zod";

const authForm = useTemplateRef("authForm");
const generalError = ref<string | null>(null);
const step = ref(0);

const items: StepperItem[] = [
  {
    title: "Informations",
    icon: "material-symbols:person-outline-rounded",
  },
  {
    title: "Sécurité",
    icon: "material-symbols:lock-outline",
  },
];

const stepperItems = computed(() =>
  items.map((item: StepperItem, i: number) => ({
    ...item,
    color: i === 0 && hasStep1Errors.value ? "error" : undefined,
  })),
);

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

const registerFields: AuthFormField[] = [
  {
    name: "name",
    type: "text",
    label: "Full Name",
    placeholder: "Enter your name",
    required: true,
  },
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

const currentFields = computed(() => {
  return registerFields.filter((field) =>
    steps[step.value]!.fields.includes(field.name),
  );
});

const stepSchemas = [
  z.object({
    name: z
      .string("Full name required")
      .min(3, "Must be at least 3 characters"),
    username: z
      .string("Username required")
      .min(3, "Must be at least 3 characters"),
    email: z.email("Invalid email"),
  }),
  z
    .object({
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
        :items="stepperItems"
        :disabled="true"
        class="w-full"
        size="sm"
      />

      <UAuthForm
        ref="authForm"
        title="Create account"
        :schema="stepSchemas[step]"
        :fields="currentFields"
        @submit="handleNext"
        loading-auto
        :submit="{
          label: isLastStep ? 'Create account' : 'Next',
          color: 'primary',
        }"
      >
        <template #description>
          Already have an account ?
          <ULink
            @click="$emit('switch-mode', 'login')"
            class="text-primary font-medium"
            >Log in</ULink
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
              label="Back"
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
