# PUNNARAJ Control Plane v0.1

This repository is the PUNNARAJ Control Plane for `punnaraj/mud`. It preserves the existing static frontend while adding Cloudflare Pages Functions under `/functions` for a bounded API layer.

## Detected build setup

- Framework: plain static root, not Vite.
- Existing frontend entrypoint: `index.html`.
- Existing build output: repository root (`.`).
- `package.json` was not present before v0.1; the added `npm run build` script is intentionally a no-op so existing static output is not rewritten.
- `_routes.json` is placed at the repository root because the Pages build output directory is `.`.

## Pages and Functions role

Cloudflare Pages serves the static repository frontend. Pages Functions handle `/api/*` only, so normal static assets and documentation paths remain static.

The root `_routes.json` keeps function invocation bounded:

- Include: `/api/*`
- Exclude: `/assets/*`, `/favicon.ico`, `/robots.txt`, `/images/*`

## API routes

| Route | Methods | Purpose |
| --- | --- | --- |
| `/api/health` | `GET` | Public health check for the control plane runtime. |
| `/api/system` | `GET` | Public safe system metadata and configured binding names only. |
| `/api/jobs` | `GET`, `POST` | List jobs or create a queued processing job. |
| `/api/jobs/:id` | `GET` | Fetch a single D1-backed processing job. |
| `/api/compile` | `POST` | Queue a compile job and dispatch to `COMPILER` when configured. |
| `/api/hooks/github` | `POST` | Receive GitHub webhooks with optional HMAC verification. |

## Cloudflare bindings

Configure these binding names in the Cloudflare Pages dashboard or a reviewed Wrangler configuration. Do not invent IDs in source control.

| Binding | Type | Required for |
| --- | --- | --- |
| `DB` | D1 database | Persistent `processing_jobs` storage. |
| `VAULT_BUCKET` | R2 bucket | Vault source object storage. |
| `ARTIFACT_BUCKET` | R2 bucket | Generated artifact storage. |
| `CONFIG` | KV namespace or JSON/text variable | Runtime configuration. |
| `COMPILER` | Service binding | Async compile dispatch. |

Optional safe text variables:

- `PUN_ENV`: environment label such as `development`, `preview`, or `production`.
- `PUN_PROJECT`: Cloudflare Pages project label such as `magga-113`.

## Secrets

Configure secrets only in Cloudflare Pages settings or local `.dev.vars`. Do not commit secret values.

- `ADMIN_TOKEN`: bearer token for `/api/admin/*`.
- `GITHUB_WEBHOOK_SECRET`: GitHub webhook HMAC secret. Required when `PUN_ENV=production`.

## D1 schema

Apply `schema/processing_jobs.sql` to the D1 database bound as `DB`.

Example:

```bash
npx wrangler d1 execute <database-name> --file=schema/processing_jobs.sql
```

## Local development

```bash
npm install
npm run build
npx wrangler pages dev . --port 8788
```

In another terminal:

```bash
curl http://localhost:8788/api/health
curl http://localhost:8788/api/system
```

Because this is a plain static root project, `npx wrangler pages dev` should also work after Wrangler reads `pages_build_output_dir` from `wrangler.jsonc`.

## Cloudflare dashboard binding checklist

- Confirm the Pages project is `magga-113`.
- Confirm build output directory is the repository root (`.`) or equivalent dashboard root output.
- Add D1 binding named `DB`.
- Apply `schema/processing_jobs.sql` to the bound D1 database.
- Add R2 bucket bindings named `VAULT_BUCKET` and `ARTIFACT_BUCKET`.
- Add `CONFIG` as a KV namespace or safe runtime variable.
- Add service binding named `COMPILER` when a compiler Worker exists.
- Add `ADMIN_TOKEN` as a secret before introducing `/api/admin/*` routes.
- Add `GITHUB_WEBHOOK_SECRET` as a secret before using GitHub webhooks in production.
- Set `PUN_ENV=production` and `PUN_PROJECT=magga-113` for production if desired.

## Deployment checklist

- Run `npm install`.
- Run `npm run build`.
- Run `python3 scripts/validators/check_repo_structure.py`.
- Run local Pages dev with `npx wrangler pages dev . --port 8788`.
- Verify `/api/health` and `/api/system` with `curl`.
- Verify D1 migration has been applied before expecting persistent jobs.
- Verify GitHub webhook secret is configured before setting `PUN_ENV=production`.
- Deploy without committing `.dev.vars`, tokens, database IDs, or generated local state.
