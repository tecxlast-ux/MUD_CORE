import { configuredBindingNames, optionalString, SERVICE } from "../_lib/env";
import type { PagesContext } from "../_lib/env";
import { json, methodNotAllowed } from "../_lib/response";

export async function onRequest(context: PagesContext): Promise<Response> {
  if (context.request.method !== "GET") {
    return methodNotAllowed(["GET"]);
  }

  const environment = optionalString(context.env.PUN_ENV);
  const project = optionalString(context.env.PUN_PROJECT);

  return json({
    ok: true,
    service: SERVICE.name,
    repo: SERVICE.repo,
    runtime: SERVICE.runtime,
    version: SERVICE.version,
    ...(environment ? { environment } : {}),
    ...(project ? { project } : {}),
    bindings: configuredBindingNames(context.env),
  });
}
