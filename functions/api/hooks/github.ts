import { verifyGitHubSignature } from "../../_lib/crypto";
import { isProduction, optionalString } from "../../_lib/env";
import type { PagesContext } from "../../_lib/env";
import { errorJson, json, methodNotAllowed } from "../../_lib/response";

export async function onRequest(context: PagesContext): Promise<Response> {
  if (context.request.method !== "POST") {
    return methodNotAllowed(["POST"]);
  }

  const body = await context.request.text();
  const secret = optionalString(context.env.GITHUB_WEBHOOK_SECRET);
  let warning: string | undefined;

  if (secret) {
    const signature = context.request.headers.get("x-hub-signature-256");
    const verified = await verifyGitHubSignature(secret, body, signature);

    if (!verified) {
      return errorJson(401, "invalid_signature", "GitHub webhook signature verification failed.");
    }
  } else if (isProduction(context.env)) {
    return errorJson(
      503,
      "webhook_secret_required",
      "GITHUB_WEBHOOK_SECRET must be configured in production.",
    );
  } else {
    warning = "GITHUB_WEBHOOK_SECRET is not configured; webhook accepted outside production.";
  }

  return json({
    ok: true,
    received: true,
    ...(warning ? { warning } : {}),
  });
}
