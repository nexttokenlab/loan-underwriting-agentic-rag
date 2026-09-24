# Explaining the architecture

## Requirement evolution

Basic retrieval answers a known question: "What income is declared?" Investigation answers a broader goal: "What evidence is required, and is it present?" The agent chooses the next query after seeing prior results. A fixed workflow remains preferable for stable, enumerable checks. Multiple agents are unnecessary for this scope.

## Division of responsibilities

Document intelligence supplies extracted fields, tables, and provenance. Retrieval selects applicant evidence and applicable policy. The LLM selects queries and tools. Server-side code filters scopes, computes ratios, validates source IDs, and limits execution. A human reviews the assessment.

## How to read the code

1. Run `python -m underwriting demo` and inspect six tool calls.
2. Read `Workspace.allowed`: scope and effective dates are applied before ranking.
3. Read `Workspace.execute`: tool arguments are validated and calculations use retrieved server data.
4. Read `run`: observations are appended as tool results and become the next model input.
5. Contrast `Replay.respond` with `Claude.respond`: only the live provider chooses actions dynamically.

## Honest interview pitch

"I built a synthetic underwriting investigation MVP inspired by PaperQA's agent loop and loan-processing reference architectures. The model can search documents and policies repeatedly based on evidence. Arithmetic, scope filters, citations, and stopping limits are enforced in code. The offline demonstration is scripted; live model quality still requires evaluation."

## Evaluation plan — not measured results

Build labeled cases for base salary, incomplete bonus history, complete history, self-employment, contradictory values, expired policy, absent documents, and embedded malicious instructions. Keep applicant fixtures out of training prompts.

Compare a single-pass RAG answer pipeline with live adaptive retrieval using the same model and corpus. Evaluate required-evidence recall, supported claims, correct missing-document identification, cross-applicant leakage, policy-version correctness, token usage, tool count, and latency. Have domain reviewers label expected evidence and acceptable conclusions. Unit-test pass rates do not establish underwriting accuracy.

## Limitations worth discussing

Lexical retrieval misses synonyms; add hybrid retrieval only after measuring recall. OCR errors require provenance and field-confidence handling upstream. Net bank credits and gross salary are not directly comparable. Citation IDs prove provenance, not support. No real jurisdiction rules or automated lending decisions are implemented. The fixture's fictional policy should never be presented as regulatory guidance.
