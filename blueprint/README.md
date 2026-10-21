# New Dash Uploader — Project Blueprint

This folder contains the proposed architecture and SDLC baseline for a new Dash upload project. It is intended to be copied into the new repository and refined with the maintainers before implementation begins.

## Documents

1. [Architecture extraction and comparison](./01-architecture-extraction.md) — extracts both existing systems and maps their observed limitations to design controls.
2. [Target architecture](./02-target-architecture.md) — defines the proposed component boundaries and end-to-end upload lifecycle.
3. [Target architecture diagram](./target-architecture.mmd) — standalone Mermaid diagram source.
4. [Product and technical requirements](./03-requirements.md) — functional, non-functional, operational, and acceptance requirements.
5. [Security and privacy threat model](./04-security-threat-model.md) — trust boundaries, threats, required controls, and security verification.
6. [Development path](./05-development-roadmap.md) — sequenced milestones, dependencies, and exit criteria.
7. [SDLC, quality, and release process](./06-sdlc-quality-and-release.md) — repository practices, CI, testing, release, and maintenance.
8. [Architecture decisions, risks, and open questions](./07-decisions-risks-and-open-questions.md) — initial ADRs, risk register, and decisions that need owner input.
9. [Existing architecture diagram](./existing-architectures.mmd) — simplified as-is diagrams for both comparison projects.

## Source basis and limits

The legacy analysis is based on the local `dash-uploader` checkout at commit `e1a1af4` and its archived README. Relevant local documentation is in [`../REPOSITORY_ANALYSIS.md`](../REPOSITORY_ANALYSIS.md).

The Uppy5 analysis is based on the public `main` branch at commit [`a71c145fa79b7459ffd83002ca301bbe670bde7e`](https://github.com/Ozx-68102/dash-uploader-uppy5/commit/a71c145fa79b7459ffd83002ca301bbe670bde7e), inspected on 2026-10-21. The repository metadata reports package version 0.3.1 and a Python minimum of 3.13 at that revision. Links in the architecture report point to the relevant source files.

This blueprint is an initial engineering proposal, not proof that the future system will have no defects or vulnerabilities. It deliberately marks deployment and product choices that need owner confirmation. Security, load, compatibility, and operational claims must be verified by tests and review before release.

## Proposed project rule

Do not start the implementation until the owners have decided the open questions in [the decision register](./07-decisions-risks-and-open-questions.md), especially the upload transport/protocol, deployment topology, authentication integration, storage backend, and supported runtime matrix.
