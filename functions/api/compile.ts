import { hasCompiler } from "../_lib/env";
import type { PagesContext, ServiceBinding } from "../_lib/env";
import { compileJobType, insertJob } from "../_lib/jobs";
import type { CompileTarget, ProcessingJob } from "../_lib/jobs";
import { errorJson, json, methodNotAllowed, readJsonObject } from "../_lib/response";

export async function onRequest(context: PagesContext): Promise<Response> {
  if (context.request.method !== "POST") {
    return methodNotAllowed(["POST"]);
  }

  const parsed = await readJsonObject(context.request);
  if (!parsed.ok) {
    return parsed.response;
  }

  const { target, path } = parsed.value;

  if (!isCompileTarget(target)) {
    return errorJson(400, "invalid_target", "Compile target must be either vault or note.");
  }

  if (path !== undefined && typeof path !== "string") {
    return errorJson(400, "invalid_path", "Compile path must be a string when provided.");
  }

  const payload = {
    target,
    ...(path ? { path } : {}),
  };

  try {
    const result = await insertJob(context.env, compileJobType(target), payload);
    const warnings = result.warning ? [result.warning] : [];
    let compilerDispatched = false;

    if (hasCompiler(context.env)) {
      compilerDispatched = true;
      const dispatch = dispatchCompiler(context.env.COMPILER, result.job).catch(() => undefined);
      if (context.waitUntil) {
        context.waitUntil(dispatch);
      } else {
        void dispatch;
      }
    } else {
      warnings.push("COMPILER service binding is not configured; compile job is queued only.");
    }

    return json(
      {
        ok: true,
        job: result.job,
        compiler: { dispatched: compilerDispatched },
        ...(warnings.length > 0 ? { warning: warnings.join(" ") } : {}),
      },
      202,
    );
  } catch {
    return errorJson(500, "compile_job_failed", "Failed to create compile job.");
  }
}

function isCompileTarget(value: unknown): value is CompileTarget {
  return value === "vault" || value === "note";
}

async function dispatchCompiler(compiler: ServiceBinding, job: ProcessingJob): Promise<void> {
  await compiler.fetch(
    new Request("https://punnaraj-control-plane.internal/compile", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        source: "punnaraj-control-plane",
        job,
      }),
    }),
  );
}
