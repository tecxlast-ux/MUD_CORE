import { SERVICE } from "../_lib/env";
import type { PagesContext } from "../_lib/env";
import { json, methodNotAllowed } from "../_lib/response";

export async function onRequest(context: PagesContext): Promise<Response> {
  if (context.request.method !== "GET") {
    return methodNotAllowed(["GET"]);
  }

  return json({
    ok: true,
    service: SERVICE.name,
    repo: SERVICE.repo,
    runtime: SERVICE.runtime,
    version: SERVICE.version,
    time: new Date().toISOString(),
  });
}
