export const useAuthStore = defineStore("auth", () => {
  const token = useCookie("auth_token", {
    maxAge: 60 * 60 * 24 * 30,
    path: "/",
    sameSite: "lax",
    secure: true,
  });
  const user = ref<Record<string, any> | null>(null);

  const isAuthenticated = computed(() => !!token.value);
  const userId = computed(() => user.value?.id ?? null);

  function setToken(newToken: string) {
    token.value = newToken;
  }

  function clearToken() {
    token.value = null;
  }

  function setUser(userData: Record<string, any>) {
    user.value = userData;
  }

  function clearUser() {
    user.value = null;
  }

  function logout() {
    clearToken();
    clearUser();
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
