---
title: Cloudflare DNS and Mail Routing
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

# Cloudflare DNS and Mail Routing

The current working boundary treats Google as identity-only and Cloudflare as routing and control layer.

This page is a beta reference, not an operational record. It must not include account details, recovery details, or vendor dashboard identifiers.

## Public-Safe Facts

- Cloudflare is the routing and control layer.
- Google is identity-only, not mail routing.
- `magga-113` is the Cloudflare Pages Control Plane and Atlas surface.
- `magga-112` is the API Gateway reference.

Operational details remain outside this public layer.
