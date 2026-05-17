---
title: Failure Recovery
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

# Failure Recovery

PUNNARAJ assumes that tools, agents, sessions, and vendors can fail.

The repository must therefore favor durable files, reproducible build steps, clear indexes, and bounded publication layers.

## Recovery Principles

- Every important context should have a file-backed recovery point.
- Agents should be able to resume from canonical and beta references.
- Build outputs should be reproducible from reviewed markdown.
- Errors should fail closed when publication safety is uncertain.
- Rollback should be possible through Git and generated artifacts.

Failure is acceptable. Unrecoverable ambiguity is not.
