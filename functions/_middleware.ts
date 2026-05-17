import type { PagesContext } from "./_lib/env";
import { optionalString } from "./_lib/env";
import { errorJson } from "./_lib/response";

export async function onRequest(context: PagesContext): Promise<Response> {
  const pathname = new URL(context.request.url).pathname;

  try {
    if (pathname === "/api/health" || pathname === "/api/system") {
      return context.next();
    }

    if (pathname.startsWith("/api/admin/")) {
      const token = optionalString(context.env.ADMIN_TOKEN);

      if (!token) {
        return errorJson(503, "admin_token_unconfigured", "Admin API token is not configured.");
      }

      const expected = `Bearer ${token}`;
      const actual = context.request.headers.get("authorization") ?? "";

      if (actual !== expected) {
        return errorJson(401, "unauthorized", "Admin API requires a valid bearer token.");
      }
    }

    return context.next();
  } catch {
    return errorJson(500, "internal_error", "Internal server error.");
  }
}
