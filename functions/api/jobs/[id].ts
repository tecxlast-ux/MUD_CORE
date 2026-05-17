import type { PagesContext } from "../../_lib/env";
import { getJobById, hasDb } from "../../_lib/jobs";
import { errorJson, json, methodNotAllowed } from "../../_lib/response";

export async function onRequest(context: PagesContext): Promise<Response> {
  if (context.request.method !== "GET") {
    return methodNotAllowed(["GET"]);
  }

  if (!hasDb(context.env)) {
    return errorJson(501, "db_not_configured", "DB binding is required to fetch a job by id.");
  }

  const id = getId(context.params);
  if (!id) {
    return errorJson(400, "missing_job_id", "Job id is required.");
  }

  try {
    const job = await getJobById(context.env, id);

    if (!job) {
      return errorJson(404, "job_not_found", "Processing job was not found.");
    }

    return json({ ok: true, job });
  } catch {
    return errorJson(500, "job_query_failed", "Failed to query processing job.");
  }
}

function getId(params: PagesContext["params"]): string | undefined {
  const raw = params?.id;
  return typeof raw === "string" && raw.length > 0 ? raw : undefined;
}
