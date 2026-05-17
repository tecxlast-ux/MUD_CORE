import type { Env } from "./env";

export const JOB_TYPES = ["compile_vault", "compile_note", "test"] as const;
export type JobType = (typeof JOB_TYPES)[number];
export type JobStatus = "queued" | "running" | "completed" | "failed";
export type CompileTarget = "vault" | "note";

export interface ProcessingJob {
  id: string;
  type: JobType;
  status: JobStatus;
  payload: Record<string, unknown>;
  result?: unknown;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

interface ProcessingJobRow {
  id: string;
  type: string;
  status: string;
  payload: string | null;
  result: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export const DB_MISSING_WARNING =
  "DB binding is not configured; using a mock queued job response.";

export function hasDb(env: Env): env is Env & { DB: NonNullable<Env["DB"]> } {
  return env.DB !== undefined && env.DB !== null;
}

export function isJobType(value: unknown): value is JobType {
  return typeof value === "string" && JOB_TYPES.includes(value as JobType);
}

export function compileJobType(target: CompileTarget): JobType {
  return target === "vault" ? "compile_vault" : "compile_note";
}

export function createJobRecord(type: JobType, payload: Record<string, unknown>): ProcessingJob {
  const now = new Date().toISOString();

  return {
    id: crypto.randomUUID(),
    type,
    status: "queued",
    payload,
    created_at: now,
    updated_at: now,
  };
}

export async function listJobs(
  env: Env,
): Promise<{ jobs: ProcessingJob[]; warning?: string }> {
  if (!hasDb(env)) {
    return {
      jobs: [],
      warning: "DB binding is not configured; returning an empty mock job list.",
    };
  }

  const result = await env.DB.prepare(
    `SELECT id, type, status, payload, result, error, created_at, updated_at
     FROM processing_jobs
     ORDER BY created_at DESC
     LIMIT 50`,
  ).all<ProcessingJobRow>();

  return {
    jobs: (result.results ?? []).map(rowToJob),
  };
}

export async function insertJob(
  env: Env,
  type: JobType,
  payload: Record<string, unknown>,
): Promise<{ job: ProcessingJob; warning?: string }> {
  const job = createJobRecord(type, payload);

  if (!hasDb(env)) {
    return { job, warning: DB_MISSING_WARNING };
  }

  await env.DB.prepare(
    `INSERT INTO processing_jobs
      (id, type, status, payload, result, error, created_at, updated_at)
     VALUES (?, ?, ?, ?, NULL, NULL, ?, ?)`,
  )
    .bind(
      job.id,
      job.type,
      job.status,
      JSON.stringify(job.payload),
      job.created_at,
      job.updated_at,
    )
    .run();

  return { job };
}

export async function getJobById(env: Env, id: string): Promise<ProcessingJob | null> {
  if (!hasDb(env)) {
    return null;
  }

  const row = await env.DB.prepare(
    `SELECT id, type, status, payload, result, error, created_at, updated_at
     FROM processing_jobs
     WHERE id = ?`,
  )
    .bind(id)
    .first<ProcessingJobRow>();

  return row ? rowToJob(row) : null;
}

function rowToJob(row: ProcessingJobRow): ProcessingJob {
  const job: ProcessingJob = {
    id: row.id,
    type: isJobType(row.type) ? row.type : "test",
    status: normaliseStatus(row.status),
    payload: parseJsonObject(row.payload),
    created_at: row.created_at,
    updated_at: row.updated_at,
  };

  if (row.result !== null) {
    job.result = parseJsonValue(row.result);
  }

  if (row.error !== null) {
    job.error = row.error;
  }

  return job;
}

function normaliseStatus(value: string): JobStatus {
  return value === "running" || value === "completed" || value === "failed"
    ? value
    : "queued";
}

function parseJsonObject(value: string | null): Record<string, unknown> {
  const parsed = parseJsonValue(value);
  return typeof parsed === "object" && parsed !== null && !Array.isArray(parsed) ? parsed : {};
}

function parseJsonValue(value: string | null): unknown {
  if (value === null || value.length === 0) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}
