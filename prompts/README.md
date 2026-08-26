# prompts/ — System prompts, curated collections, and examples

This directory stores system prompts, templates, and curated prompt collections used by TensorVault. Prompts live in category folders (system, curated, examples) and every prompt file must include clear metadata for provenance, intended model family, recommended parameters, and safety guidance.

Top-level layout
- prompts/
  - README.md                <- this file (organization & contribution standards)
  - system/                  <- vendor/family-specific system prompts
    - openai/
    - anthropic/
    - llama/
  - curated/                 <- hand-picked prompt collections for tasks (e.g., summarization, code-gen)
  - examples/                <- runnable examples and notebooks demonstrating usage
  - templates/               <- reusable prompt skeletons and templates

File formats
- Prompts may be stored in YAML (.yaml/.yml) or JSON (.json). YAML is preferred for readability.
- Each prompt file should be a single document (YAML mapping / JSON object) containing both metadata and the prompt body.

Required metadata (per prompt file)
- id: machine-friendly id (lowercase, alphanum, dash/underscore)
- title: short human-readable title
- purpose: brief one-line statement of what this prompt is for
- model_family: recommended model family or compatibility note (e.g., `openai/gpt-4`, `llama-2-13b`)
- prompt: string or array of strings composing the system / user instruction(s)
- recommended_parameters: object containing suggested runtime params:
  - temperature: number (0.0 - 2.0)
  - top_p: number (0.0 - 1.0)
  - max_tokens: optional integer
- safety_notes: short advisory about known failure modes, sensitivity, and PII/privacy guidance
- license: SPDX id or link (optional but recommended)
- author/contact: optional attribution/maintainer info
- created_at / updated_at: ISO 8601 timestamps (recommended)

Example metadata skeleton (YAML)
```yaml
id: "summarize-technical"
title: "Summarize technical content"
purpose: "Produce concise technical summaries suitable for engineers"
model_family: "decoder-only (GPT-style)"
prompt: |
  You are a helpful assistant that summarizes technical documents...
recommended_parameters:
  temperature: 0.2
  top_p: 0.95
  max_tokens: 300
safety_notes: |
  Avoid hallucinations; when unsure, respond with "Insufficient information".
license:
  id: "CC-BY-4.0"
author:
  name: "ACME AI"
created_at: "2026-08-26T12:00:00Z"
