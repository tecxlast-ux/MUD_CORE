---
title: Vendor Boundary
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

# Vendor Boundary

Vendors are adapters, not sovereigns.

Cloud services, identity providers, AI platforms, and hosting systems can provide useful interfaces, but the PUNNARAJ structure must remain portable and understandable without vendor lock-in.

## Current Boundary

- Google is identity-only, not mail routing.
- Cloudflare is the routing and control layer.
- Cloudflare Pages project `magga-113` is the publication surface for this repository.
- `magga-112` is treated as API Gateway context.

The durable structure lives in reviewed files and published references, not inside a vendor dashboard.
