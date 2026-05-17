import type { PagesContext } from "../../_lib/env";
import { hasDb } from "../../_lib/jobs";
import { insertJob, isJobType, listJobs } from "../../_lib/jobs";
import { errorJson, isPlainObject, json, methodNotAllowed, readJsonObject } from "../../_lib/response";

export async function onRequest(context: PagesContext): Promise<Response> {
  if (context.request.method === "GET") {
    return handleGet(context);
  }

  if (context.request.method === "POST") {
    return handlePost(context);
  }

  return methodNotAllowed(["GET", "POST"]);
}

async function handleGet(context: PagesContext): Promise<Response> {
  try {
    const result = await listJobs(context.env);
    return json({
      ok: true,
      jobs: result.jobs,
      ...(result.warning ? { warning: result.warning } : {}),
    });
  } catch {
    return errorJson(500, "jobs_query_failed", "Failed to query processing jobs.");
  }
}

async function handlePost(context: PagesContext): Promise<Response> {
  const parsed = await readJsonObject(context.request);
  if (!parsed.ok) {
    return parsed.response;
  }

  const { type, payload } = parsed.value;

  if (!isJobType(type)) {
    return errorJson(
      400,
      "invalid_job_type",
      "Job type must be one of: compile_vault, compile_note, test.",
    );
  }

  if (payload !== undefined && !isPlainObject(payload)) {
    return errorJson(400, "invalid_payload", "Job payload must be a JSON object.");
  }

  try {
    const result = await insertJob(context.env, type, payload ?? {});
    return json(
      {
        ok: true,
        job: result.job,
        ...(result.warning ? { warning: result.warning } : {}),
      },
      hasDb(context.env) ? 201 : 202,
    );
  } catch {
    return errorJson(500, "job_insert_failed", "Failed to create processing job.");
  }
}
