from pathlib import Path
from langchain_core.messages import HumanMessage
from agent import build_agent, WORKSPACE
from evaluator import evaluate

IDEA = Path(WORKSPACE, "ideas", "idea.md")
REPORT = Path(WORKSPACE, "output", "review.md")
IMPROVED = Path(WORKSPACE, "output", "idea_improved.md")
MAX_ATTEMPTS = 3


def print_tool_calls(messages):
    for m in messages:
        for c in getattr(m, "tool_calls", None) or []:
            path = c["args"].get("file_path", "")
            tag = "SKILL" if "/skills/" in path else "tool "
            print(f"   {tag}: {c['name']:12} {path}")


def main():
    idea_text = IDEA.read_text()
    agent = build_agent()
    messages = [
        HumanMessage(
            "Review the idea in /ideas/idea.md. Write /output/review.md and /output/idea_improved.md."
        )
    ]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n--- Attempt {attempt} ---")
        seen = len(messages)
        result = agent.invoke(
            {"messages": messages},
            config={
                "run_name": f"agent attempt {attempt}",
                "tags": ["idea-stress-tester", "agent-loop"],
            },
        )
        print_tool_calls(result["messages"][seen:])
        messages = result["messages"]

        verdict = evaluate(idea_text, REPORT.read_text(), IMPROVED.read_text())
        if verdict.passed:
            print("✓ Verifier passed")
            break

        print("✗ Verifier found issues:")
        for issue in verdict.issues:
            print("   -", issue)
        feedback = "Fix these issues with edit_file:\n" + "\n".join(verdict.issues)
        messages.append(HumanMessage(feedback))
    else:
        print("Stopped: max attempts reached")

    print(f"\nBefore: {IDEA}\nAfter:  {IMPROVED}\nReport: {REPORT}")


if __name__ == "__main__":
    main()
