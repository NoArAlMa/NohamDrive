import { runtimeState } from "../../state/runtime";

export default defineEventHandler(async (event) => {
  const body = await readBody(event);

  runtimeState.host = body.host;
  runtimeState.port = body.port;
  runtimeState.token = body.token;
  runtimeState.started_at = body.started_at;

  return { ok: true };
});
