# PUNNARAJ Publishing Workflow

This repository is a public publication surface for reviewed PUNNARAJ reference material. It is not the Zero Vault and it is not the final source of truth.

## Layer Model

### Zero Vault

Zero Vault is the private raw source layer. It may contain raw capsules, raw chats, raw transcripts, sensitive evidence, recovery details, and operational context. It must not be published from this repository.

### Notebook Compression Outputs

Notebook outputs are compression inputs. They can help digest raw capsules into structured objects, summaries, and derived thoughts, but they are not automatically beta or public material.

### Beta Reference Layer

The Beta Reference Layer is reviewed working context. It is public-readable, marked beta, and designed for humans and agents who need current operational understanding without access to private raw evidence.

### Project Atlas

The Project Atlas is the public presentation layer. It explains PUNNARAJ clearly for outsiders while staying subordinate to reviewed source material.

## Publication Rules

- Raw transcripts must not be published.
- Raw chats must not be published.
- Secrets, credentials, account recovery details, and operationally sensitive records must not be published.
- Private emails must not be published beyond public role labels.
- Derived notes must not be treated as canon without human validation.
- Public pages must declare frontmatter metadata before they are built.

## Promotion Flow

```text
raw -> compressed -> reviewed beta -> public atlas
```

1. Capture the raw capsule in the private source layer.
2. Compress the raw capsule into structured objects or notes.
3. Review the compressed object for public safety and usefulness.
4. Promote reviewed working context into `content/beta/`.
5. Promote stable public explanation into `content/public/`.
6. Run `npm run validate:public` before publishing.
7. Run `npm run build` to generate `/beta/` and `/atlas/`.

## Human Review Gate

Human review is required before derived material becomes canonical. The build process can block obvious unsafe strings, missing metadata, and non-public visibility, but it cannot decide final authority.
