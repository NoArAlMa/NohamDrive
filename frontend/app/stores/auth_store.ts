export const useAuthStore = defineStore("auth", () => {
  const { reset } = useFileTree();

  const token = useCookie("auth_token", {
    maxAge: 60 * 60 * 24 * 30,
    path: "/",
    sameSite: "lax",
    secure: true,
  });

  watch(token, (newVal) => {
    if (!newVal) {
      reset();
    }
  });

  const userCookie = useCookie<User | null>("user_data", {
    maxAge: 60 * 60 * 24 * 30,
    path: "/",
    sameSite: "lax",
    secure: true,
  });

  const user = ref<User | null>(userCookie.value ?? null);

  // Computed
  const isAuthenticated = computed(() => !!token.value);
  const userId = computed(() => user.value?.id ?? null);

  // Actions
  function setToken(newToken: string) {
    token.value = newToken;
  }

  function clearToken() {
    token.value = null;
  }

  function setUser(userData: User) {
    user.value = userData;
    userCookie.value = userData;
  }

  function clearUser() {
    user.value = null;
    userCookie.value = null;
  }

  function logout() {
    clearToken();
    clearUser();
  }

  // Hydratation côté client (si reload)
  if (!user.value && userCookie.value) {
    user.value = userCookie.value;
  }

  return {
    token,
    user,
    isAuthenticated,
    userId,
    setToken,
    clearToken,
    setUser,
    clearUser,
    logout,
  };
});
