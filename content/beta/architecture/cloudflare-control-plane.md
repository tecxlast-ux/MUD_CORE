---
title: Cloudflare Control Plane
layer: beta
status: beta
visibility: public
source_layer: reviewed_derived
confidence: medium
last_reviewed: 2026-05-17
owner: Wisut Punnaraj
tags:
  - punnaraj
---

# Cloudflare Control Plane

This repository is deployed as Cloudflare Pages project `magga-113`.

Within the current architecture, `magga-113` acts as Control Plane and Project Atlas surface. It hosts static pages and Pages Functions without becoming the source of truth.

## Boundaries

- Preserve existing frontend content.
- Preserve existing API routes and Pages Functions.
- Generate public-safe reference HTML from reviewed markdown.
- Do not invent Cloudflare identifiers.
- Keep routing and publication roles explicit.

The Control Plane should make the system legible while keeping raw evidence private.
