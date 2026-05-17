const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
};

export function json(data: unknown, init: number | ResponseInit = 200): Response {
  const responseInit = typeof init === "number" ? { status: init } : init;
  const headers = new Headers(responseInit.headers);

  for (const [key, value] of Object.entries(JSON_HEADERS)) {
    if (!headers.has(key)) {
      headers.set(key, value);
    }
  }

  return new Response(JSON.stringify(data, null, 2), {
    ...responseInit,
    headers,
  });
}

export function errorJson(
  status: number,
  code: string,
  message: string,
  extra?: Record<string, unknown>,
  headers?: HeadersInit,
): Response {
  return json(
    {
      ok: false,
      error: {
        code,
        message,
        ...(extra ?? {}),
      },
    },
    { status, headers },
  );
}

export function methodNotAllowed(allowed: string[]): Response {
  return errorJson(
    405,
    "method_not_allowed",
    `Method not allowed. Allowed methods: ${allowed.join(", ")}.`,
    { allowed },
    { allow: allowed.join(", ") },
  );
}

export async function readJsonObject(
  request: Request,
): Promise<{ ok: true; value: Record<string, unknown> } | { ok: false; response: Response }> {
  let parsed: unknown;

  try {
    parsed = await request.json();
  } catch {
    return {
      ok: false,
      response: errorJson(400, "invalid_json", "Request body must be valid JSON."),
    };
  }

  if (!isPlainObject(parsed)) {
    return {
      ok: false,
      response: errorJson(400, "invalid_body", "Request body must be a JSON object."),
    };
  }

  return { ok: true, value: parsed };
}

export function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
