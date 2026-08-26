# TensorVault

[Badge placeholders: build | lint | license]

TensorVault is a curated, auditable, and community-friendly repository for AI system prompts, open-weights model metadata, and project documentation. Our goal is to make it easy to share, discover, and validate prompts and model resources while enforcing provenance, licensing clarity, and reproducible metadata—without hosting large model weights inside the repo.

Key principles
- Transparency: every model or prompt must include clear provenance and licensing metadata.
- Safety & Privacy: prompts and metadata must follow our safety guidelines (see docs/prompt-guidelines.md).
- Reproducibility: metadata includes reproducible checks (checksums, manifests, config references).
- Minimal weight hosting: weights are referenced (URLs/manifests) and must include integrity checks; weights themselves are not stored here.

Quick links
- docs/ — documentation and governance
- prompts/ — organized system prompts, templates, and examples
- models/ — metadata, manifests, and config pointers for models
- scripts/ — helpful scripts (validation, index building)
- .github/workflows/ — CI for linting and automatic validation

Repository layout (short)
- .github/workflows/
  - ci.yml — main continuous integration (runs tests, metadata validators)
  - lint-md.yml — Markdown linting and link checks
  - validate-model-metadata.yml — validates model YAML/JSON metadata and manifests
  - prompt-lint.yml — optional prompt linter
- docs/ — human-facing docs: architecture, metadata schemas, governance, FAQs
- prompts/
  - system/ — vendor / family-specific prompts (subfolders per family/provider)
  - curated/ — curated prompt collections and templates
  - examples/ — small examples showing usage patterns
- models/
  - manifests/ — top-level index of available models (index.yaml)
  - metadata/ — per-model metadata files (YAML/JSON) describing source, license, checksums, config
  - configs/ — model-specific config snippets (e.g., tokenizer/config references)
  - weights-pointers/ — manifests or pointer files that describe where weights live (with integrity info)
- scripts/ — small tools for maintainers and contributors (validation, indexing)
- tests/ — unit/integration checks for metadata and prompt linters
- assets/ — logos, diagrams used in docs or README

Why not store weights in-repo?
We store metadata and manifests that point to externally hosted weights (S3 / huggingface / other registries). Each weight pointer MUST include:
- canonical URL(s)
- filename(s)
- file size(s)
- cryptographic checksum(s) (SHA256 preferred)
- host and license information
This approach keeps the repo lightweight and ensures legal and licensing checks are explicit.

Model metadata schema (example)
See docs/metadata-schemas.md for the authoritative version. Minimum recommended fields (YAML example):

```yaml
name: "example-model"
version: "0.1.0"
display_name: "Example Model v0.1"
description: "Short one-line description"
license:
  id: "Apache-2.0"
  url: "https://www.apache.org/licenses/LICENSE-2.0"
provenance:
  source: "https://huggingface.co/org/example-model"
  fetched_at: "2026-08-26T12:00:00Z"
weights:
  - filename: "example-model-weights.pt"
    url: "https://storage.example.com/example-model-weights.pt"
    sha256: "012345abcdef..."
    size_bytes: 123456789
config:
  architecture: "transformer"
  params: 1_000_000_000
tags:
  - llm
  - decoder-only
