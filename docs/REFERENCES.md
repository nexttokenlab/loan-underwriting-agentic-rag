# Architectural references

This project contains original code and synthetic fixtures. No source code, applicant data, prompts, or policies were copied from these repositories. They are credited as conceptual inspiration, not incorporated dependencies:

- [FutureHouse PaperQA](https://github.com/Future-House/paper-qa): separation of search, evidence gathering, and answer generation, orchestrated by an agent.
- [Amey-Mohite Agentic RAG Financial](https://github.com/Amey-Mohite/agentic-rag-financial): bounded document-retrieval loop and source tracking. Our MVP does not implement its advertised hybrid retrieval stack.
- [Red Hat Multi-Agent Loan Origination](https://github.com/rh-ai-quickstart/multi-agent-loan-origination): underwriting domain tools, role boundaries, and advisory assessment workflows. Its prescribed risk-assessment sequence is not evidence of this project's adaptive retrieval loop.

[Anthropic tool definitions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) document the live adapter's tool protocol.

If incorporating upstream code later, inspect the license at the specific revision and preserve all required notices. This repository intentionally has no redistribution license selected yet; the owner can choose one before public release.
