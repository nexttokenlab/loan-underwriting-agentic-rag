import argparse
import json
import sys
from .core import Workspace, run
from .models import Claude, Replay

def main():
    p = argparse.ArgumentParser(description="Synthetic underwriting evidence investigation")
    p.add_argument("mode", choices=["demo", "live", "baseline"])
    p.add_argument("--application", default="APP-001")
    p.add_argument("--as-of", default="2026-09-24")
    p.add_argument("--max-calls", type=int, default=10)
    p.add_argument("--question", default="Review income evidence against applicable policy and identify missing supporting evidence.")
    args = p.parse_args()
    if args.mode == "demo" and (args.application != "APP-001" or args.as_of != "2026-09-24"):
        p.error("Replay uses only APP-001 on 2026-09-24; use live or baseline for other inputs")
    try:
        ws = Workspace(args.application, args.as_of)
        if args.mode == "baseline":
            result = {"mode": "single_pass_retrieval_baseline", "question": args.question,
                      "evidence": ws.search(args.question),
                      "note": "Retrieval-only baseline: no answer model and no adaptive policy search."}
        else:
            result = run(Replay() if args.mode == "demo" else Claude(), ws, args.question, args.max_calls)
            result["mode"] = "scripted_replay_not_autonomous" if args.mode == "demo" else "live_agent"
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print("Run failed: " + type(exc).__name__ + ". Check configuration, model access, application ID, and network. No decision produced.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
