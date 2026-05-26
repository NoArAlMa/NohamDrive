<script setup lang="ts">
import type { GenericAPIResponse } from "~~/shared/types/API";
import type { User } from "~~/shared/types/auth";

const { $getLocale, switchLocale, t: i18nT } = useI18n();
const t = (...args: Parameters<typeof i18nT>) => i18nT(...args) as string;

definePageMeta({
  layout: "default",
  middleware: "auth-middleware",
});

useHead(() => ({
  title: t("settings.headTitle"),
  meta: [
    {
      name: "NohamDrive | Settings",
      content: t("settings.description"),
    },
  ],
}));

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
    localPath: string;
    startOnStartup: boolean;
    syncOnMetered: boolean;
    intervalMinutes: 5 | 15 | 30 | 60;
    lastSyncAt: string | null;
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
    localPath: "~/NohamDrive",
    startOnStartup: false,
    syncOnMetered: false,
    intervalMinutes: 15,
    lastSyncAt: null,
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

settings.value = {
  ...DEFAULT_SETTINGS,
  ...settings.value,
  appearance: { ...DEFAULT_SETTINGS.appearance, ...settings.value.appearance },
  account: { ...DEFAULT_SETTINGS.account, ...settings.value.account },
  general: { ...DEFAULT_SETTINGS.general, ...settings.value.general },
  notifications: {
    ...DEFAULT_SETTINGS.notifications,
    ...settings.value.notifications,
  },
  sync: { ...DEFAULT_SETTINGS.sync, ...settings.value.sync },
  security: { ...DEFAULT_SETTINGS.security, ...settings.value.security },
  privacy: { ...DEFAULT_SETTINGS.privacy, ...settings.value.privacy },
};

const colorMode = useColorMode();

watch(
  () => settings.value.appearance.theme,
  (next) => {
    colorMode.preference = next;
  },
  { immediate: true },
);

watch(
  () => settings.value.general.language,
  (next) => {
    if (next && next !== $getLocale()) {
      switchLocale(next);
    }
  },
  { immediate: true },
);

const authStore = useAuthStore();
const { user, profilePictureUrl } = storeToRefs(authStore);
const toast = useToast();

const resetOpen = ref(false);

function resetSettings() {
  settings.value = structuredClone(DEFAULT_SETTINGS);
  resetOpen.value = false;
}

const profilePictureOpen = ref(false);

const avatarSrc = computed(() => profilePictureUrl.value || undefined);

function onProfilePictureUpdated() {
  authStore.bumpAvatar();
}

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
const profileSaving = ref(false);

async function saveProfile() {
  profileSaved.value = false;
  profileError.value = null;

  if (!user.value) {
    profileError.value = t("settings.errors.noUser");
    return;
  }

  if (!profileDraft.username.trim()) {
    profileError.value = t("settings.errors.usernameRequired");
    return;
  }

  if (!profileDraft.email.trim() || !profileDraft.email.includes("@")) {
    profileError.value = t("settings.errors.emailInvalid");
    return;
  }

  if (!profileDraft.full_name.trim()) {
    profileError.value = t("settings.errors.fullNameRequired");
    return;
  }

  profileSaving.value = true;
  try {
    const response = await $fetch<GenericAPIResponse<User>>("/api/users/me", {
      method: "PATCH",
      body: {
        username: profileDraft.username.trim(),
        email: profileDraft.email.trim(),
        full_name: profileDraft.full_name.trim(),
      },
    });

    if (response.data) {
      authStore.setUser(response.data);
    }

    profileSaved.value = true;
    toast.add({
      title: t("settings.profileSaved"),
      color: "success",
      icon: "material-symbols:check-rounded",
    });
    setTimeout(() => (profileSaved.value = false), 1500);
  } catch (error: any) {
    profileError.value =
      error?.data?.message ?? error?.message ?? "Unable to save profile.";
  } finally {
    profileSaving.value = false;
  }
}

const avatarInput = ref<HTMLInputElement | null>(null);

const passwordDraft = reactive({
  current_password: "",
  new_password: "",
  confirm_password: "",
});

const passwordError = ref<string | null>(null);
const passwordSaved = ref(false);
const passwordSaving = ref(false);

async function savePassword() {
  passwordSaved.value = false;
  passwordError.value = null;

  if (!passwordDraft.current_password) {
    passwordError.value = t("settings.errors.currentPasswordRequired");
    return;
  }

  if (passwordDraft.new_password !== passwordDraft.confirm_password) {
    passwordError.value = t("settings.errors.newPasswordsMismatch");
    return;
  }

  passwordSaving.value = true;
  try {
    await $fetch<GenericAPIResponse<null>>("/api/users/password", {
      method: "PATCH",
      body: {
        current_password: passwordDraft.current_password,
        new_password: passwordDraft.new_password,
      },
    });

    passwordDraft.current_password = "";
    passwordDraft.new_password = "";
    passwordDraft.confirm_password = "";
    passwordSaved.value = true;
    toast.add({
      title: t("settings.passwordSection.updatedTitle"),
      color: "success",
      icon: "material-symbols:check-rounded",
    });
    setTimeout(() => (passwordSaved.value = false), 1500);
  } catch (error: any) {
    passwordError.value =
      error?.data?.message ?? error?.message ?? "Unable to update password.";
  } finally {
    passwordSaving.value = false;
  }
}

const syncPathError = computed<string | boolean | undefined>(() => {
  const path = settings.value.sync.localPath?.trim() ?? "";
  const pathWithoutDrive = path.replace(/^[A-Za-z]:[\\/]/, "");

  if (!path) return "Choose a local folder before enabling sync.";
  if (/[<>:"|?*]/.test(pathWithoutDrive)) {
    return "This path contains characters that are not supported.";
  }

  return undefined;
});

const syncReady = computed(
  () => settings.value.sync.autoSync && !syncPathError.value,
);
const lastSyncLabel = computed(() => {
  if (!settings.value.sync.lastSyncAt) return t("settings.sync.notSyncedYet");
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(settings.value.sync.lastSyncAt));
});

function resetSyncPath() {
  settings.value.sync.localPath = DEFAULT_SETTINGS.sync.localPath;
}

function markSyncNow() {
  if (!syncReady.value) return;
  settings.value.sync.lastSyncAt = new Date().toISOString();
  toast.add({
    title: t("settings.sync.queued"),
    color: "primary",
    icon: "material-symbols:sync-rounded",
  });
}

const themeOptions = computed<{ label: string; value: ThemePreference }[]>(
  () => [
    { label: t("settings.theme.system"), value: "system" },
    { label: t("settings.theme.light"), value: "light" },
    { label: t("settings.theme.dark"), value: "dark" },
  ],
);

const languageOptions = computed<{ label: string; value: "en" | "fr" }[]>(
  () => [
    { label: t("language.fr"), value: "fr" },
    { label: t("language.en"), value: "en" },
  ],
);

const folderInput = ref<HTMLInputElement | null>(null);

function openFolderPicker() {
  folderInput.value?.click();
}

function onFolderPicked(event: Event) {
  const input = event.target as HTMLInputElement;

  if (!input.files?.length) return;

  const firstFile = input.files[0];

  // Récupère le chemin du dossier racine
  const relativePath = firstFile!.webkitRelativePath;

  const folderName = relativePath.split("/")[0];

  settings.value.sync.localPath = folderName!;
}
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
            {{ t("settings.actions.reset") }}
          </UButton>
          <UButton
            color="primary"
            variant="subtle"
            icon="material-symbols:shield-outline-rounded"
            to="/settings#security"
          >
            {{ t("settings.actions.security") }}
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
            <h2 class="text-lg font-semibold">
              {{ t("settings.sections.userSettings") }}
            </h2>
          </div>
        </template>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div class="lg:col-span-1">
            <div class="flex items-center gap-4">
              <UAvatar
                :alt="profileDraft.full_name || 'User'"
                :src="avatarSrc"
                size="3xl"
              />
              <div class="flex flex-col gap-2">
                <UButton
                  color="neutral"
                  variant="soft"
                  icon="material-symbols:photo-camera-outline-rounded"
                  @click="profilePictureOpen = true"
                >
                  {{ t("settings.profile.changePhoto") }}
                </UButton>
              </div>
            </div>
            <p class="mt-3 text-sm text-muted">
              {{ t("settings.profile.detailsHint") }}
            </p>
          </div>

          <LazySettingsProfilePicture
            v-model:open="profilePictureOpen"
            @updated="onProfilePictureUpdated"
          />

          <div class="lg:col-span-2 space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <UFormField :label="t('settings.profile.username')">
                <UInput
                  v-model="profileDraft.username"
                  :placeholder="t('settings.profile.placeholderUsername')"
                />
              </UFormField>
              <UFormField :label="t('settings.profile.email')">
                <UInput
                  v-model="profileDraft.email"
                  type="email"
                  :placeholder="t('settings.profile.placeholderEmail')"
                />
              </UFormField>
            </div>

            <UFormField :label="t('settings.profile.fullName')">
              <UInput
                v-model="profileDraft.full_name"
                :placeholder="t('settings.profile.placeholderFullName')"
              />
            </UFormField>

            <div class="flex flex-wrap items-center gap-2 justify-end">
              <UAlert
                v-if="profileError"
                color="error"
                variant="subtle"
                :title="t('settings.profile.notSaved')"
                :description="profileError"
                class="w-full md:w-auto"
              />
              <UAlert
                v-else-if="profileSaved"
                color="success"
                variant="subtle"
                :title="t('settings.profile.savedTitle')"
                :description="t('settings.profile.savedDesc')"
                class="w-full md:w-auto"
              />
              <UButton
                color="primary"
                variant="subtle"
                icon="material-symbols:save-outline-rounded"
                :loading="profileSaving"
                @click="saveProfile"
              >
                {{ t("settings.profile.save") }}
              </UButton>
            </div>
          </div>
        </div>
      </UCard>

      <UCard class="lg:col-span-2">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="material-symbols:password-rounded" class="size-5" />
            <h2 class="text-lg font-semibold">
              {{ t("settings.sections.password") }}
            </h2>
          </div>
        </template>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div>
            <p class="text-sm text-muted">
              {{ t("settings.passwordSection.hint") }}
            </p>
          </div>

          <div class="lg:col-span-2 space-y-4">
            <UFormField :label="t('settings.passwordSection.current')">
              <UInput
                v-model="passwordDraft.current_password"
                type="password"
                autocomplete="current-password"
                :placeholder="t('settings.passwordSection.placeholderCurrent')"
              />
            </UFormField>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <UFormField :label="t('settings.passwordSection.new')">
                <UInput
                  v-model="passwordDraft.new_password"
                  type="password"
                  autocomplete="new-password"
                  :placeholder="t('settings.passwordSection.placeholderNew')"
                />
              </UFormField>
              <UFormField :label="t('settings.passwordSection.confirm')">
                <UInput
                  v-model="passwordDraft.confirm_password"
                  type="password"
                  autocomplete="new-password"
                  :placeholder="
                    t('settings.passwordSection.placeholderConfirm')
                  "
                />
              </UFormField>
            </div>

            <div class="flex flex-wrap items-center gap-2 justify-end">
              <UAlert
                v-if="passwordError"
                color="error"
                variant="subtle"
                :title="t('settings.passwordSection.notUpdated')"
                :description="passwordError"
                class="w-full md:w-auto"
              />
              <UAlert
                v-else-if="passwordSaved"
                color="success"
                variant="subtle"
                :title="t('settings.profile.savedTitle')"
                :description="t('settings.passwordSection.savedDesc')"
                class="w-full md:w-auto"
              />
              <UButton
                color="primary"
                variant="subtle"
                icon="material-symbols:lock-reset-rounded"
                :loading="passwordSaving"
                @click="savePassword"
              >
                {{ t("settings.passwordSection.update") }}
              </UButton>
            </div>
          </div>
        </div>
      </UCard>

      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="material-symbols:palette-outline" class="size-5" />
            <h2 class="text-lg font-semibold">
              {{ t("settings.sections.appearance") }}
            </h2>
          </div>
        </template>

        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <UFormField
              :label="t('settings.appearance.theme')"
              :description="t('settings.appearance.themeDesc')"
            >
              <USelect
                v-model="settings.appearance.theme"
                :items="themeOptions"
              />
            </UFormField>

            <UFormField
              :label="t('settings.appearance.language')"
              :description="t('settings.appearance.languageDesc')"
            >
              <USelect
                v-model="settings.general.language"
                :items="languageOptions"
              />
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
            <h2 class="text-lg font-semibold">
              {{ t("settings.sections.notifications") }}
            </h2>
          </div>
        </template>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <UFormField
            :label="t('settings.notifications.desktop')"
            :description="t('settings.notifications.desktopDesc')"
          >
            <USwitch v-model="settings.notifications.desktop" />
          </UFormField>
          <UFormField
            :label="t('settings.notifications.sounds')"
            :description="t('settings.notifications.soundsDesc')"
          >
            <USwitch v-model="settings.notifications.sounds" />
          </UFormField>
          <UFormField
            :label="t('settings.notifications.syncAlerts')"
            :description="t('settings.notifications.syncAlertsDesc')"
          >
            <USwitch v-model="settings.notifications.syncAlerts" />
          </UFormField>
        </div>
      </UCard>

      <UCard>
        <template #header>
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <UIcon name="material-symbols:sync-rounded" class="size-5" />
              <h2 class="text-lg font-semibold">
                {{ t("settings.sections.sync") }}
              </h2>
            </div>
            <UBadge :color="syncReady ? 'success' : 'neutral'" variant="subtle">
              {{
                syncReady ? t("settings.sync.ready") : t("settings.sync.paused")
              }}
            </UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <div class="rounded-lg border border-muted bg-muted/20 p-3">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-default truncate">
                  {{
                    settings.sync.localPath ||
                    t("settings.sync.noFolderSelected")
                  }}
                </p>
                <p class="text-xs text-muted">
                  {{ t("settings.sync.lastSync", { label: lastSyncLabel }) }}
                </p>
              </div>
              <UButton
                color="primary"
                variant="soft"
                icon="material-symbols:sync-rounded"
                :disabled="!syncReady"
                @click="markSyncNow"
              >
                {{ t("settings.sync.syncNow") }}
              </UButton>
            </div>
          </div>

          <UFormField
            :label="t('settings.sync.storagePath')"
            :description="t('settings.sync.storagePathDesc')"
            :error="syncPathError"
          >
            <div class="flex flex-col gap-2 sm:flex-row">
              <input
                ref="folderInput"
                type="file"
                webkitdirectory
                directory
                multiple
                class="hidden"
                @change="onFolderPicked"
              />

              <UInput
                v-model="settings.sync.localPath"
                class="flex-1"
                :placeholder="t('settings.sync.chooseFolder')"
                icon="material-symbols:folder-outline-rounded"
                readonly
              />

              <UButton
                color="primary"
                variant="soft"
                icon="material-symbols:folder-open-rounded"
                @click="openFolderPicker"
              >
                {{ t("common.browse") }}
              </UButton>

              <UButton
                color="neutral"
                variant="soft"
                icon="material-symbols:restart-alt-rounded"
                @click="resetSyncPath"
              >
                {{ t("common.default") }}
              </UButton>
            </div>
          </UFormField>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <UFormField
              :label="t('settings.sync.autoSync')"
              :description="t('settings.sync.autoSyncDesc')"
            >
              <USwitch v-model="settings.sync.autoSync" />
            </UFormField>
            <UFormField
              :label="t('settings.sync.startup')"
              :description="t('settings.sync.startupDesc')"
            >
              <USwitch
                v-model="settings.sync.startOnStartup"
                :disabled="!settings.sync.autoSync"
              />
            </UFormField>

            <UFormField
              :label="t('settings.sync.metered')"
              :description="t('settings.sync.meteredDesc')"
            >
              <USwitch
                v-model="settings.sync.syncOnMetered"
                :disabled="!settings.sync.autoSync"
              />
            </UFormField>
          </div>
        </div>
      </UCard>

      <UCard class="lg:col-span-2">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="material-symbols:lock-outline" class="size-5" />
            <h2 class="text-lg font-semibold">
              {{ t("settings.sections.privacy") }}
            </h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <UFormField
            :label="t('settings.privacy.analytics')"
            :description="t('settings.privacy.analyticsDesc')"
          >
            <USwitch v-model="settings.privacy.analytics" />
          </UFormField>

          <UFormField
            :label="t('settings.privacy.crashReports')"
            :description="t('settings.privacy.crashReportsDesc')"
          >
            <USwitch v-model="settings.privacy.crashReports" />
          </UFormField>
        </div>
      </UCard>
    </div>

    <UModal
      v-model:open="resetOpen"
      :title="t('settings.reset.title')"
      :description="t('settings.reset.desc')"
    >
      <template #content>
        <UCard>
          <div class="flex items-start gap-3">
            <UIcon
              name="material-symbols:warning-rounded"
              class="size-6 text-warning"
            />
            <div class="min-w-0">
              <p class="font-medium text-default">
                {{ t("settings.reset.areYouSure") }}
              </p>
              <p class="text-sm text-muted">
                {{ t("settings.reset.detail") }}
              </p>
            </div>
          </div>

          <div class="mt-5 flex justify-end gap-2">
            <UButton color="neutral" variant="ghost" @click="resetOpen = false">
              {{ t("common.cancel") }}
            </UButton>
            <UButton
              color="error"
              variant="subtle"
              icon="material-symbols:restart-alt-rounded"
              @click="resetSettings"
            >
              {{ t("settings.reset.action") }}
            </UButton>
          </div>
        </UCard>
      </template>
    </UModal>
  </div>
</template>
