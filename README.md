# Codex Skills & AGENTS.md

A curated collection of custom skills and system instructions (`AGENTS.md`) for OpenAI Codex and AI coding agents.

---

## 📋 Table of Contents

- [AGENTS.md Overview](#agentsmd-overview)
- [Skills Catalog](#skills-catalog)
- [Installation & Usage](#installation--usage)
  - [Installing Skills](#installing-skills)
  - [Using AGENTS.md](#using-agentsmd)
- [Repository Structure](#repository-structure)
- [License](#license)

---

## 🧠 AGENTS.md Overview

The root [`AGENTS.md`](./AGENTS.md) contains core operational guidelines, independent technical judgment standards, and sub-agent routing policies:

- **First Principles & Best Practices**: Strict derivation of solutions from verified evidence and invariants before considering proposals.
- **System Design Principles**: Minimal abstractions, clear component purpose, and avoiding unnecessary fallback or redundant defensive code.
- **Sub-Agent Routing Policy**: Defined role boundaries and model assignments (e.g. exploration, test execution, browser E2E, code review).
- **Harness & Planning Workflow Standards**: Integration with structured delivery phases, plan templates, and QA validation.
- **Infrastructure Safety Constraints**: Safeguards around cloud (AWS/K8s/DB) environments.

---

## 🛠 Skills Catalog

| Skill | Description |
|---|---|
| **[ai-slop-cleaner](./skills/ai-slop-cleaner)** | Regression-tests-first cleanup/refactor workflow to remove AI-generated slop, dead code, and bloated wrappers while preserving behavior. |
| **[analyze](./skills/analyze)** | Read-only deep repository analysis returning ranked synthesis with explicit confidence and evidence-vs-inference boundaries. |
| **[autopilot](./skills/autopilot)** | Bounded autonomous delivery workflow spanning clarified requirements, consensus planning, implementation, code review, and QA execution. |
| **[autoresearch](./skills/autoresearch)** | Bounded research loop with an explicit validator, evidence-gated completion, and goal tracking. |
| **[best-practice-research](./skills/best-practice-research)** | Source-backed best-practice research combining official external evidence and repo-local facts. |
| **[code-review](./skills/code-review)** | Comprehensive code review assessing quality, security, and maintainability with severity-rated feedback. |
| **[deep-interview](./skills/deep-interview)** | Intent-first requirements interview with high-value questions before planning or implementation to prevent scope drift. |
| **[hatch-pet](./skills/hatch-pet)** | Create, repair, validate, visually QA, and package Codex-compatible v2 animated desktop pets (8x11 sprite atlas). |
| **[init-harness](./skills/init-harness)** | Centralized workflow harness router for phase contracts, planning shapes, TDD, and QA rules. |
| **[pdf](./skills/pdf)** | Read, create, render (Poppler), and verify PDF files programmatically with Python tools (`reportlab`, `pdfplumber`, `pypdf`). |
| **[performance-goal](./skills/performance-goal)** | Evaluator-gated performance optimization workflow with measurable baselines and reversible increments. |
| **[plan](./skills/plan)** | Native planning workflow supporting general, consensus, and strict high-risk modes. |
| **[qa-execute](./skills/qa-execute)** | Execute frozen QA manifests with minimal context, machine-checked assertions, and evidence-only reporting. |
| **[skill](./skills/skill)** | Local Codex skill lifecycle management (listing, inspecting, creating, editing, validating, and backing up skill folders). |
| **[speech](./skills/speech)** | Spoken audio generation (TTS voiceovers, accessibility reads, IVR prompts) via OpenAI Audio API CLI. |
| **[transcribe](./skills/transcribe)** | Audio transcription and speaker diarization via OpenAI Whisper/Audio CLI with structured JSON or text output. |

---

## 🚀 Installation & Usage

### Installing Skills

To install any skill into your local Codex environment (`~/.codex/skills/`):

#### Method 1: Direct Copy / Clone
Copy the desired skill directory to `~/.codex/skills/`:
```bash
# Clone the repository
git clone https://github.com/c47-dev/skills.git

# Copy all skills or a specific skill
cp -R skills/* ~/.codex/skills/
# or
cp -R skills/ai-slop-cleaner ~/.codex/skills/
```

#### Method 2: Using Codex Skill Installer
```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo c47-dev/skills \
  --path skills/<skill-name>
```

### Using AGENTS.md

You can place `AGENTS.md` in your global Codex configuration directory or in individual project roots:
- **Global**: `cp AGENTS.md ~/.codex/AGENTS.md`
- **Project Root**: `cp AGENTS.md /path/to/your/project/AGENTS.md`

---

## 📂 Repository Structure

```text
skills/
├── AGENTS.md
├── README.md
└── skills/
    ├── ai-slop-cleaner/
    ├── analyze/
    ├── autopilot/
    ├── autoresearch/
    ├── best-practice-research/
    ├── code-review/
    ├── deep-interview/
    ├── hatch-pet/
    ├── init-harness/
    ├── pdf/
    ├── performance-goal/
    ├── plan/
    ├── qa-execute/
    ├── skill/
    ├── speech/
    └── transcribe/
```

---

## 📄 License

MIT License

