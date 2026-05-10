<script setup lang="ts">
definePageMeta({
  layout: "default",
  middleware: "auth-middleware",
});

useHead({
  title: "Settings - NohamDrive",
  meta: [
    {
      name: "NohamDrive | Settings",
      content: "Customize your NohamDrive experience",
    },
  ],
});

type ThemePreference = "system" | "light" | "dark";
type StartPage = "home" | "explorer" | "terminal";

type UserSettings = {
  appearance: {
    theme: ThemePreference;
    reducedMotion: boolean;
    compactSidebar: boolean;
    showFilePreviews: boolean;
  };
  account: {
    avatarDataUrl: string | null;
  };
  general: {
    language: "en" | "fr";
    startPage: StartPage;
    openLinksInNewTab: boolean;
  };
  notifications: {
    desktop: boolean;
    sounds: boolean;
    syncAlerts: boolean;
  };
  sync: {
    autoSync: boolean;
    syncOnMetered: boolean;
    intervalMinutes: 5 | 15 | 30 | 60;
  };
  security: {
    lockOnIdle: boolean;
    idleMinutes: 1 | 5 | 10 | 30;
    requireReauthForSensitiveActions: boolean;
  };
  privacy: {
    analytics: boolean;
    crashReports: boolean;
  };
};

const DEFAULT_SETTINGS: UserSettings = {
  appearance: {
    theme: "system",
    reducedMotion: false,
    compactSidebar: false,
    showFilePreviews: true,
  },
  account: {
    avatarDataUrl: null,
  },
  general: {
    language: "fr",
    startPage: "explorer",
    openLinksInNewTab: true,
  },
  notifications: {
    desktop: true,
    sounds: true,
    syncAlerts: true,
  },
  sync: {
    autoSync: true,
    syncOnMetered: false,
    intervalMinutes: 15,
  },
  security: {
    lockOnIdle: true,
    idleMinutes: 10,
    requireReauthForSensitiveActions: true,
  },
  privacy: {
    analytics: false,
    crashReports: true,
  },
};

const settings = useLocalStorage<UserSettings>(
  "nohamdrive.settings",
  DEFAULT_SETTINGS,
  { deep: true },
);

const colorMode = useColorMode();

watch(
  () => settings.value.appearance.theme,
  (next) => {
    colorMode.preference = next;
  },
  { immediate: true },
);

const authStore = useAuthStore();
const { user } = storeToRefs(authStore);

const resetOpen = ref(false);

function resetSettings() {
  settings.value = structuredClone(DEFAULT_SETTINGS);
  resetOpen.value = false;
}

const avatarFallbackUrl =
  "https://i.pinimg.com/736x/be/a3/49/bea3491915571d34a026753f4a872000.jpg";

const avatarSrc = computed(() => {
  return avatarFallbackUrl;
});

const profileDraft = reactive({
  username: "",
  email: "",
  full_name: "",
});

watch(
  user,
  (u) => {
    profileDraft.username = u?.username ?? "";
    profileDraft.email = u?.email ?? "";
    profileDraft.full_name = u?.full_name ?? "";
  },
  { immediate: true },
);

const profileError = ref<string | null>(null);
const profileSaved = ref(false);

function saveProfile() {
  profileSaved.value = false;
  profileError.value = null;

  if (!user.value) {
    profileError.value = "No user loaded.";
    return;
  }

  if (!profileDraft.username.trim()) {
    profileError.value = "Username is required.";
    return;
  }

  if (!profileDraft.email.trim() || !profileDraft.email.includes("@")) {
    profileError.value = "A valid email is required.";
    return;
  }

  if (!profileDraft.full_name.trim()) {
    profileError.value = "Full name is required.";
    return;
  }

  authStore.setUser({
    ...user.value,
    username: profileDraft.username.trim(),
    email: profileDraft.email.trim(),
    full_name: profileDraft.full_name.trim(),
  });

  profileSaved.value = true;
  setTimeout(() => (profileSaved.value = false), 1500);
}

// function removeAvatar() {
//   settings.value.account.avatarDataUrl = null;
// }

const avatarInput = ref<HTMLInputElement | null>(null);

// function pickAvatar() {
//   avatarInput.value?.click();
// }

// async function onAvatarPicked(event: Event) {
//   profileError.value = null;
//   const input = event.target as HTMLInputElement | null;
//   const file = input?.files?.[0];
//   if (!file) return;

//   if (!file.type.startsWith("image/")) {
//     profileError.value = "Please select an image file.";
//     return;
//   }

//   if (file.size > 3 * 1024 * 1024) {
//     profileError.value = "Image too large (max 3MB).";
//     return;
//   }

//   const dataUrl = await new Promise<string>((resolve, reject) => {
//     const reader = new FileReader();
//     reader.onerror = () => reject(new Error("Failed to read image"));
//     reader.onload = () => resolve(String(reader.result));
//     reader.readAsDataURL(file);
//   });

//   settings.value.account.avatarDataUrl = dataUrl;
//   if (input) input.value = "";
// }

const themeOptions: { label: string; value: ThemePreference }[] = [
  { label: "System", value: "system" },
  { label: "Light", value: "light" },
  { label: "Dark", value: "dark" },
];

const languageOptions: { label: string; value: "EN" | "FR" }[] = [
  { label: "Français", value: "FR" },
  { label: "English", value: "EN" },
];

const startPageOptions: { label: string; value: StartPage }[] = [
  { label: "Explorer", value: "explorer" },
  { label: "Home", value: "home" },
  { label: "Terminal", value: "terminal" },
];

const syncIntervalOptions: {
  label: string;
  value: UserSettings["sync"]["intervalMinutes"];
}[] = [
  { label: "Every 5 minutes", value: 5 },
  { label: "Every 15 minutes", value: 15 },
  { label: "Every 30 minutes", value: 30 },
  { label: "Every 60 minutes", value: 60 },
];
</script>

<template>
  <div class="px-4 laptop:px-2 py-6">
    <section
      class="relative overflow-hidden rounded-2xl border border-muted bg-linear-to-br from-primary/10 via-transparent to-secondary/10 p-6"
    >
      <div
        class="absolute -top-20 -right-20 size-64 rounded-full bg-primary/10 blur-3xl"
      />
      <div
        class="absolute -bottom-28 -left-24 size-72 rounded-full bg-secondary/10 blur-3xl"
      />

      <div class="relative flex flex-col gap-4 md:flex-row md:items-center">
        <div class="flex items-center gap-4">
          <UAvatar
            :alt="user?.full_name ?? 'User'"
            :src="avatarSrc"
            size="3xl"
          />
          <div class="min-w-0">
            <h1 class="text-2xl md:text-3xl font-bold text-default truncate">
              Settings
            </h1>
            <p class="text-sm text-muted truncate">
              {{ user?.full_name ?? "Your account" }}
              <span v-if="user?.email">· {{ user.email }}</span>
            </p>
          </div>
        </div>

        <div class="md:ml-auto flex flex-wrap gap-2">
          <UButton
            color="neutral"
            variant="soft"
            icon="material-symbols:restart-alt-rounded"
            @click="resetOpen = true"
          >
            Reset
          </UButton>
          <UButton
            color="primary"
            variant="subtle"
            icon="material-symbols:shield-outline-rounded"
            to="/settings#security"
          >
            Security
          </UButton>
        </div>
      </div>
    </section>

    <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
      <UCard class="lg:col-span-2">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon
              name="material-symbols:person-outline-rounded"
              class="size-5"
            />
            <h2 class="text-lg font-semibold">User settings</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div class="lg:col-span-1">
            <div class="flex items-center gap-4">
              <UAvatar
                :alt="profileDraft.full_name || 'User'"
                :src="avatarSrc"
                size="xl"
              />
              <div class="flex flex-col gap-2">
                <input
                  ref="avatarInput"
                  type="file"
                  accept="image/*"
                  class="hidden"
                />
                <UButton
                  color="neutral"
                  variant="soft"
                  icon="material-symbols:photo-camera-outline-rounded"
                >
                  Change photo
                </UButton>
                <UButton
                  color="neutral"
                  variant="ghost"
                  icon="material-symbols:delete-outline-rounded"
                >
                  Remove
                </UButton>
              </div>
            </div>
            <p class="mt-3 text-sm text-muted">
              Frontend only: updates are stored locally (cookie / localStorage).
            </p>
          </div>

          <div class="lg:col-span-2 space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <UFormField label="Username">
                <UInput
                  v-model="profileDraft.username"
                  placeholder="username"
                />
              </UFormField>
              <UFormField label="Email">
                <UInput
                  v-model="profileDraft.email"
                  type="email"
                  placeholder="you@domain.com"
                />
              </UFormField>
            </div>

            <UFormField label="Full name">
              <UInput
                v-model="profileDraft.full_name"
                placeholder="Full name"
              />
            </UFormField>

            <div class="flex flex-wrap items-center gap-2 justify-end">
              <UAlert
                v-if="profileError"
                color="error"
                variant="subtle"
                title="Profile not saved"
                :description="profileError"
                class="w-full md:w-auto"
              />
              <UAlert
                v-else-if="profileSaved"
                color="success"
                variant="subtle"
                title="Saved"
                description="Profile updated locally."
                class="w-full md:w-auto"
              />
              <UButton
                color="primary"
                variant="subtle"
                icon="material-symbols:save-outline-rounded"
                @click="saveProfile"
              >
                Save profile
              </UButton>
            </div>
          </div>
        </div>
      </UCard>

      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon
              name="material-symbols:palette-outline-rounded"
              class="size-5"
            />
            <h2 class="text-lg font-semibold">Appearance</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <UFormField label="Theme" description="System, light or dark">
              <USelect
                v-model="settings.appearance.theme"
                :options="themeOptions"
                option-attribute="label"
                value-attribute="value"
              />
            </UFormField>

            <UFormField label="Language" description="UI language">
              <USelect
                v-model="settings.general.language"
                :options="languageOptions"
                option-attribute="label"
                value-attribute="value"
              />
            </UFormField>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <UFormField label="Color mode" description="Quick toggle">
              <div class="flex justify-end">
                <UColorModeSwitch />
              </div>
            </UFormField>
          </div>
        </div>
      </UCard>

      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon
              name="material-symbols:notifications-outline-rounded"
              class="size-5"
            />
            <h2 class="text-lg font-semibold">Notifications</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <UFormField label="Desktop" description="Toasts & banners">
            <USwitch v-model="settings.notifications.desktop" />
          </UFormField>
          <UFormField label="Sounds" description="Subtle alerts">
            <USwitch v-model="settings.notifications.sounds" />
          </UFormField>
          <UFormField label="Sync alerts" description="Upload/download status">
            <USwitch v-model="settings.notifications.syncAlerts" />
          </UFormField>
        </div>
      </UCard>

      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="material-symbols:sync-rounded" class="size-5" />
            <h2 class="text-lg font-semibold">Sync</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <UFormField label="Auto-sync" description="Keep files up to date">
              <USwitch v-model="settings.sync.autoSync" />
            </UFormField>
            <UFormField
              label="Storage Path"
              description="The path where the files should go"
            >
              <UInput />
            </UFormField>
            <UFormField
              label="Start app on startup"
              description="Whether or not the app should be start when the computer starts-up"
            >
              <USwitch />
            </UFormField>

            <UFormField
              label="Metered connection"
              description="Allow sync on metered networks"
            >
              <USwitch v-model="settings.sync.syncOnMetered" />
            </UFormField>
          </div>

          <UFormField label="Sync interval" description="How often to sync">
            <USelect
              v-model="settings.sync.intervalMinutes"
              :disabled="!settings.sync.autoSync"
              :options="syncIntervalOptions"
              option-attribute="label"
              value-attribute="value"
            />
          </UFormField>
        </div>
      </UCard>

      <UCard class="lg:col-span-2">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon
              name="material-symbols:lock-outline-rounded"
              class="size-5"
            />
            <h2 class="text-lg font-semibold">Privacy</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <UFormField label="Analytics" description="Helps improve the product">
            <USwitch v-model="settings.privacy.analytics" />
          </UFormField>

          <UFormField
            label="Crash reports"
            description="Send anonymous diagnostics"
          >
            <USwitch v-model="settings.privacy.crashReports" />
          </UFormField>

          <UFormField label="Export settings" description="Local only">
            <UButton
              color="neutral"
              variant="soft"
              icon="material-symbols:download-rounded"
              @click="
                navigator.clipboard?.writeText(
                  JSON.stringify(settings, null, 2),
                )
              "
            >
              Copy JSON
            </UButton>
          </UFormField>
        </div>
      </UCard>
    </div>

    <UModal
      v-model:open="resetOpen"
      title="Reset settings"
      description="This will restore the default preferences on this device."
    >
      <template #content>
        <UCard>
          <div class="flex items-start gap-3">
            <UIcon
              name="material-symbols:warning-rounded"
              class="size-6 text-warning"
            />
            <div class="min-w-0">
              <p class="font-medium text-default">Are you sure?</p>
              <p class="text-sm text-muted">
                This only affects the current browser / desktop app profile. No
                server data is changed.
              </p>
            </div>
          </div>

          <div class="mt-5 flex justify-end gap-2">
            <UButton color="neutral" variant="ghost" @click="resetOpen = false">
              Cancel
            </UButton>
            <UButton
              color="error"
              variant="subtle"
              icon="material-symbols:restart-alt-rounded"
              @click="resetSettings"
            >
              Reset
            </UButton>
          </div>
        </UCard>
      </template>
    </UModal>
  </div>
</template>
