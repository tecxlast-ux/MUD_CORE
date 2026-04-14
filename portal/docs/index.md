# MUD_CORE Documentation Portal

Welcome to the official documentation portal for **Punnaraj Digital Heritage**—a long-term knowledge and governance system designed to preserve identity, intent, methodologies, and strategic continuity across generations.

## Purpose

MUD_CORE serves as the operational memory layer for the Punnaraj ecosystem. This portal presents the repository in a structured, searchable interface without changing the canonical source layout used for authoring.

- **Single Source of Truth (SSOT):** All original documents remain in their existing repository folders.
- **Portal Layer:** This MkDocs site is generated from a temporary, build-time copy for clean governance.
- **Continuity-first Design:** Manifest, methodology, references, and archival records remain navigable as one coherent system.

## Documentation Architecture

The portal organizes content into two primary domains:

1. **Core System**
   - Manifest and identity definitions
   - Methodological standards and verification processes
   - Program deliverables, references, and archives
2. **SSOT**
   - Canonical supporting knowledge domains
   - Domain-specific readme documents and snapshots

## Governance Principles

- **No relocation of source files** in the main repository structure.
- **Build-time virtual injection** copies source folders into `portal/docs/` during CI only.
- **Traceable publication pipeline** via GitHub Actions to GitHub Pages.

## What You Can Do Here

- Browse the full hierarchy from the left navigation panel.
- Use global search to find terms across all Markdown and text documents.
- Access living documentation published from the latest `main` branch.

---

**Project:** Punnaraj Digital Heritage  
**Portal:** MUD_CORE (MkDocs Material)
