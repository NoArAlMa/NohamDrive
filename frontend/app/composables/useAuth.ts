import type { AuthResponse } from "~~/shared/types/auth";

export const useAuth = () => {
  const { setToken, clearToken, setUser, clearUser, logout } = useAuthStore();

  const toast = useToast();

  const handleBackendError = (backend: any): AuthResponse => {
    if (backend?.statusCode === 422 && backend?.data) {
      return {
        success: false,
        fieldErrors: Object.entries(backend.data).map(([name, message]) => ({
          name,
          message: String(message),
        })),
        message: backend.message,
        statusCode: backend.statusCode,
      };
    }

    return {
      success: false,
      message: backend?.message ?? "Une erreur inattendue est survenue",
      statusCode: backend?.statusCode,
    };
  };

  async function loginUser(
    payload: UserLoginPayload,
  ): Promise<AuthResponse<AuthUserResponse>> {
    try {
      const response = await $fetch<GenericAPIResponse<AuthUserResponse>>(
        "/auth/login",
        {
          method: "POST",
          body: payload,
        },
      );

      if (response.data) {
        setToken(response.data.token.token);
        setUser(response.data.user);
      }

      toast.add({
        title: "Login successful !",
        color: "success",
        icon: "material-symbols:check-rounded",
      });

      return { success: true, data: response.data!, message: response.message };
    } catch (error: any) {
      return handleBackendError(error?.data);
    }
  }

  async function registerUser(
    payload: UserCreatePayload,
  ): Promise<AuthResponse<AuthUserResponse>> {
    try {
      const { password, ...rest } = payload;
      const cleanedData = { ...rest, password };

      const response = await $fetch<GenericAPIResponse<AuthUserResponse>>(
        "/auth/register",
        {
          method: "POST",
          body: cleanedData,
        },
      );

      if (response.data) {
        setToken(response.data.token.token);
        setUser(response.data.user);
      }

      toast.add({
        title: "Account created !",
        color: "success",
        icon: "material-symbols:check-rounded",
      });

      return { success: true, data: response.data!, message: response.message };
    } catch (error: any) {
      return handleBackendError(error?.data);
    }
  }

  return {
    loginUser,
    registerUser,
  };
};
