export const SERVICE = {
  name: "punnaraj-control-plane",
  repo: "punnaraj/mud",
  runtime: "cloudflare-pages-functions",
  version: "0.1.0",
} as const;

export interface D1PreparedStatement {
  bind(...values: unknown[]): D1PreparedStatement;
  first<T = Record<string, unknown>>(): Promise<T | null>;
  all<T = Record<string, unknown>>(): Promise<{ results?: T[] }>;
  run(): Promise<unknown>;
}

export interface D1Database {
  prepare(query: string): D1PreparedStatement;
}

export interface ServiceBinding {
  fetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response>;
}

export interface Env {
  DB?: D1Database;
  VAULT_BUCKET?: unknown;
  ARTIFACT_BUCKET?: unknown;
  CONFIG?: unknown;
  COMPILER?: ServiceBinding;
  ADMIN_TOKEN?: string;
  GITHUB_WEBHOOK_SECRET?: string;
  PUN_ENV?: string;
  PUN_PROJECT?: string;
  [key: string]: unknown;
}

export interface PagesContext {
  request: Request;
  env: Env;
  params?: Record<string, string | string[]>;
  next: () => Promise<Response>;
  waitUntil?: (promise: Promise<unknown>) => void;
}

const SAFE_BINDINGS = [
  "DB",
  "VAULT_BUCKET",
  "ARTIFACT_BUCKET",
  "CONFIG",
  "COMPILER",
] as const;

export function configuredBindingNames(env: Env): string[] {
  return SAFE_BINDINGS.filter((name) => env[name] !== undefined && env[name] !== null);
}

export function optionalString(value: unknown): string | undefined {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

export function isProduction(env: Env): boolean {
  return optionalString(env.PUN_ENV) === "production";
}

export function hasCompiler(env: Env): env is Env & { COMPILER: ServiceBinding } {
  return typeof env.COMPILER?.fetch === "function";
}
