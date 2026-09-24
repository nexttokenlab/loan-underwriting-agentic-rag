"""Live tool calling and an explicitly scripted offline teaching replay."""
import json
import os
import urllib.request

class Claude:
    def __init__(self):
        self.key = os.environ["ANTHROPIC_API_KEY"]
        self.model = os.environ["ANTHROPIC_MODEL"]

    def respond(self, messages, tools, system):
        body = json.dumps({"model": self.model, "max_tokens": 2048,
            "system": system, "messages": messages, "tools": tools}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
            headers={"x-api-key": self.key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.load(response)
        if payload.get("stop_reason") == "max_tokens":
            raise RuntimeError("Model response truncated; no assessment accepted")
        return payload["content"]

class Replay:
    """Fixture actions; deliberately NOT an autonomous agent or quality evaluation."""
    def __init__(self):
        self.index = 0
        self.actions = [
            ("search_documents", {"query": "income salary bonus"}),
            ("search_policy", {"query": "bonus history income"}),
            ("search_documents", {"query": "annual bonus history 2024 2025"}),
            ("list_documents", {}),
            ("calculate_dti", {"source_id": "A1-APPLICATION"}),
            ("submit_assessment", {
                "summary": "Declared income includes variable bonus. Only 2025 bonus history is present; fictional policy requires two completed years. Declared-income DTI is 30.00%, not a verified eligibility result.",
                "citations": ["A1-APPLICATION", "A1-BONUS-2025", "P-BONUS-V2"],
                "missing_evidence": ["2024 bonus history supporting the variable-income assessment"]}),
        ]
    def respond(self, messages, tools, system):
        name, args = self.actions[self.index]
        self.index += 1
        return [{"type": "tool_use", "id": "replay-"+str(self.index), "name": name, "input": args}]
