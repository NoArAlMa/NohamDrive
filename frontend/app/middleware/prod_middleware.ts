export default defineNuxtRouteMiddleware(() => {
  if (process.env.NODE_ENV === "production") {
    throw createError({
      statusCode: 404,
      message: "Page not found",
    });
  }
});
