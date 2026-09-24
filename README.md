# Loan Underwriting Agentic RAG


## Start in 30 seconds

Python 3.9+; no runtime packages or API key required for the teaching replay:

```bash
python -m underwriting demo
python -m unittest discover -s tests -v
python -m underwriting baseline --question "What income and bonus does the applicant declare?"
```

Run commands from the repository root. The demo prints each tool call, evidence, and the final assessment. It follows a **scripted replay**, not an autonomous agent and not proof of model quality. The baseline retrieves applicant passages once; it is a retrieval-only comparator, not a full RAG answer benchmark.

## Real agent mode

```bash
export ANTHROPIC_API_KEY='your-key'
export ANTHROPIC_MODEL='your-tool-capable-model-id'
python -m underwriting live --application APP-001 --max-calls 10
```

Use a model available in your Anthropic account. `.env` files are not automatically loaded. Live mode sends questions and retrieved synthetic content to Anthropic and incurs API costs. It uses the Messages API with tool definitions and feeds tool results back into model context. The model chooses the queries and action order. Live provider behavior has not been validated with credentials in this project; offline tests validate the execution contract only.

## System architecture

The current implementation is a Python CLI with an in-memory document corpus and a bounded tool-calling loop. In live mode, Claude selects the next action; Python executes it and returns the evidence for the next model turn.

```mermaid
flowchart TB
  U[Underwriter question and application ID] --> CLI[Python CLI]
  CLI --> W[Workspace: applicant, product, assessment date]
  CLI --> LOOP[Bounded agent loop]
  LOOP --> MODEL[Claude Messages API in live mode]
  MODEL --> CALL[Selected tool and arguments]
  CALL --> CHECK[Validate tool, arguments, repetition and budget]
  CHECK --> DOC[search_documents]
  CHECK --> POL[search_policy]
  CHECK --> INV[list_documents]
  CHECK --> CALC[calculate_dti]
  CHECK --> FINAL[submit_assessment]
  DATA[(Synthetic extracted pages and policy versions)] --> W
  W --> DOC
  W --> POL
  W --> INV
  W --> CALC
  DOC --> OBS[Tool results and evidence IDs]
  POL --> OBS
  INV --> OBS
  CALC --> OBS
  OBS --> LOOP
  FINAL --> CITE[Validate citation IDs against retrieved evidence]
  CITE --> OUT[Advisory assessment and execution trace]
  LOOP --> STOP[Budget exhausted or no validated submission]
  STOP --> REVIEW[Human review required]
  OUT --> REVIEW
```

### Components and responsibilities

| Component | Implementation | Responsibility |
|---|---|---|
| Entry point | [`underwriting/__main__.py`](underwriting/__main__.py) | Select mode, application, assessment date, question, and tool-call budget. |
| Agent controller | [`run`](underwriting/core.py) | Send observations back to the model, execute selected tools, and enforce stopping limits. |
| Model adapter | [`Claude`](underwriting/models.py) | Call the external model with message history and tool schemas; return its chosen actions. |
| Evidence workspace | [`Workspace`](underwriting/core.py) | Restrict document access to the selected applicant and policies to the product and effective date. |
| Retrieval | `Workspace.search` | Rank eligible pages by lexical term overlap, return up to three matches, and record retrieved IDs. |
| Calculation | `calculate_dti` | Read financial fields from an authorized, previously retrieved source and calculate with `Decimal`. |
| Assessment validation | `submit_assessment` | Require retrieved citation IDs and mark the result as requiring human review. |
| Trace | `run` return value | Record tool names, arguments, and results in the CLI's JSON output. This is not persistent audit storage. |

### Data and retrieval boundaries

The MVP starts with **pre-extracted pages** in [`data/corpus.json`](data/corpus.json). Each record has a source ID, title, page number, and text. Applicant records have an application ID; policy records have a product and effective interval.

```text
Applicant search:
  selected application → filter its pages → rank matches → return evidence

Policy search:
  application's product + assessment date → filter applicable policies
  → rank matches → return evidence
```

Filtering happens before ranking. Policy intervals include `effective_from` and exclude `effective_to`. The selected application is a local CLI scope; a future API must derive this scope from authenticated access rights. There is no database, OCR service, embedding model, or vector index in the current implementation.

### Agent state and stopping behavior

State exists in memory for one run:

- **Message history:** the question, model tool calls, and tool results.
- **Retrieved evidence IDs:** used to reject citations to unseen sources.
- **Action fingerprints:** used to reject identical repeated tool calls.
- **Execution trace:** tool arguments and results, including validation errors.
- **Tool-call budget:** counts individual calls, even when a model requests several together.

A successful `submit_assessment` ends the loop. If the budget runs out or the model ends without a validated submission, the system returns a human-review status and trace. Repeated or invalid tool calls return an error observation so the model can change its action within the remaining budget. Provider failures exit the CLI without an assessment.

### Execution modes

| Mode | Who chooses actions? | What it demonstrates |
|---|---|---|
| `live` | The language model, after observing tool results. | Adaptive retrieval architecture; requires provider credentials. |
| `demo` | A predefined replay in Python. | A reproducible example and execution-contract checks; not autonomous reasoning. |
| `baseline` | A fixed single applicant-document search. | Retrieval-only comparison; no generated answer or policy investigation. |

### Planned ingestion and retrieval extensions

The following pipeline is a **future extension**, not an implemented capability:

```mermaid
flowchart LR
  PDF[PDFs and scans] -.-> OCR[OCR and layout extraction]
  OCR -.-> CHUNK[Section and table-aware chunks]
  CHUNK -.-> META[Source pages, applicant scope and policy metadata]
  META -.-> INDEX[Keyword and vector indexes]
  INDEX -.-> RET[Hybrid retrieval with reranking]
  RET -.-> TOOLS[Existing document and policy tool interfaces]
```

The agent/tool boundary allows retrieval to improve without replacing the investigation loop. Further extensions include authenticated access, durable audit storage, a full single-pass RAG answer baseline, and labeled model-quality evaluations.

## Why it is agentic

The original requirement was to answer a specific question from an applicant's documents. A single retrieval could support that task. The expanded requirement is to determine which evidence is still needed under applicable policy. Discovering a bonus can cause a policy search, and the policy can cause a search for historical statements.

```mermaid
flowchart TD
  Q[Underwriter question] --> M[Model chooses next tool]
  M --> D[Search applicant documents]
  M --> P[Search applicable policy]
  M --> I[Inspect document inventory]
  M --> C[Deterministic calculation]
  D --> O[Return evidence to model]
  P --> O
  I --> O
  C --> O
  O --> M
  M --> F[Submit cited advisory assessment]

```

The loop in `underwriting/core.py:run` is the agentic mechanism. It does not contain a bonus-specific branch. `models.py:Replay` deliberately does; it exists solely to teach and test the loop without an API key.

## Example investigation

1. Find declared income including a variable bonus.
2. Retrieve the fictional policy requiring two completed years of bonus history.
3. Search for historical statements.
4. Inspect the inventory: only 2025 is present.
5. Calculate an illustrative declared-income DTI from server-read fields.
6. Report missing 2024 history with citations for underwriter review.

A declared-income ratio is not verified qualifying income. The app never approves or denies a loan.

## What is implemented

- Two isolated synthetic applicant scopes and policy product/date filtering.
- Auditable tool arguments, results, and document/page references.
- Lexical term-overlap retrieval, with deterministic ranking; no embeddings or vector database yet.
- Decimal arithmetic reading authorized retrieved fixture values.
- Citation-ID provenance checking, unknown-tool/argument rejection, repeated-call detection, and an individual tool-call budget.
- Live Claude tool-use adapter, scripted offline replay, unit tests, GitHub Actions.

The CLI's application selection is a local demo scope, **not authentication**. A service deployment must derive allowed application IDs from authenticated permissions. Citation validation checks that a source was retrieved; it does not verify semantic entailment. Prompt instructions are not a complete prompt-injection defense.

## Layout

| File | Purpose |
|---|---|
| `underwriting/core.py` | Retrieval, tool definitions, validations, and agent loop |
| `underwriting/models.py` | Live provider and offline replay |
| `underwriting/__main__.py` | CLI |
| `data/corpus.json` | Synthetic extracted pages and fictional policy versions |
| `tests/test_core.py` | Execution and boundary tests |
| `docs/INTERVIEW.md` | Architecture explanation and evaluation plan |
| `docs/REFERENCES.md` | Inspiration and attribution |

## Scope and next steps

This is a small original MVP inspired by three architectures, not a merger or fork of their implementations. It consumes pre-extracted pages; PDF/OCR ingestion, layout-aware chunking, hybrid retrieval, full answer baseline, and model-quality evaluation remain extensions. No production lending accuracy or compliance claim is made.

See [interview notes](docs/INTERVIEW.md) and [references](docs/REFERENCES.md).
