# PUNNARAJ Reference Layers

This repository builds two public-safe static surfaces from reviewed markdown:

- `/beta/` - Beta Reference Layer for reviewed working context.
- `/atlas/` - Project Atlas for public presentation.

The source markdown lives under `content/beta/` and `content/public/`.

## Status Values

- `beta` - reviewed enough for working coordination, still open to correction.
- `reviewed` - checked and stable enough for broader reuse.
- `canonical` - human-validated source of authority.
- `public` - intended for public presentation.

## Required Frontmatter

Every source markdown file must begin with:

```yaml
---
title:
layer: beta | public
status: beta | reviewed | canonical | public
visibility: public
source_layer: reviewed_derived | compressed | manual
confidence: low | medium | high
last_reviewed: 2026-05-17
owner: Wisut Punnaraj
tags:
  - punnaraj
---
```

The builder rejects files without required frontmatter, files whose `visibility` is not `public`, unsupported status values, unsupported confidence values, and source files containing obvious unsafe publication strings.

## Safety Validator

`scripts/build_reference_layers.py` uses only the Python standard library. It validates:

- required frontmatter keys,
- layer consistency with the source directory,
- `visibility: public`,
- supported `status`, `source_layer`, and `confidence` values,
- ISO-style `last_reviewed`,
- required `punnaraj` tag,
- obvious unsafe publication strings in source content.

The validator is a publication guard, not a substitute for human review.

## Build Commands

```bash
npm run validate:public
npm run build:reference
npm run build:atlas
npm run build:beta
npm run build
```

`npm run build` runs the existing repository validator, builds both reference surfaces, and runs the repository validator again.

## Generated Output

The builder generates static HTML:

- `beta/index.html`
- nested pages under `beta/`
- `atlas/index.html`
- nested pages under `atlas/`

Each generated page includes automatic navigation, status badges, sitemap-style index cards, and footer metadata for layer, status, source layer, confidence, review date, and owner.
