# Domain docs

## Before exploring the codebase

This repository uses a single-context layout.

- Read `GLOSSARY.md` at the repository root.
- Read relevant architecture decision records in `docs/adr/`.

If these files are absent, proceed silently. The domain-modeling skill
creates them when terms or decisions are resolved.

## File structure

- `GLOSSARY.md`: shared domain terms.
- `docs/adr/NNNN-short-title.md`: architecture decision records.

## Use the glossary's vocabulary

Use defined terms in issue titles, proposals, hypotheses, and tests.
When a needed concept is absent, reconsider the term or note the gap
for domain-modeling.

## Flag ADR conflicts

When a proposal contradicts an existing ADR, identify the ADR and
explain why its decision should be reconsidered.
