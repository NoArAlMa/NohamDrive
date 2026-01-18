export default defineNuxtRouteMiddleware(() => {
  if (process.env.NODE_ENV === "production") {
    throw createError({
      statusCode: 404,
      statusMessage: "Page not found",
    });
  }
});
