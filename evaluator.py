from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from agent import MODEL

RUBRIC = """You are a strict reviewer of an idea review. Pass ONLY if ALL are true:
1. Section 1 (What is clear) contains only things the idea text actually says.
2. Every item in Vague claims quotes words that really appear in the idea.
3. There are at least 3 assumptions, each specific to this idea.
4. There are at least 5 clarification questions, each specific to this idea.
5. idea_improved.md adds no new numbers, features, or claims. Unknowns appear as [PLACEHOLDER: ...].
6. If the idea involves AI, hardware, education, or social impact, at least one assumption or question addresses that domain specifically.
List every failed point as an issue. Each issue must name the file and section to fix.
If everything passes, return passed=true and an empty issues list."""


class Verdict(BaseModel):
    passed: bool = Field(description="True only if every rubric point passes")
    issues: list[str] = Field(description="Specific fixes needed, empty if passed")


def evaluate(idea: str, report: str, improved: str) -> Verdict:
    judge = init_chat_model(MODEL, temperature=0).with_structured_output(Verdict)
    prompt = (
        f"{RUBRIC}\n\nIDEA:\n{idea}\n\nREPORT:\n{report}\n\nIMPROVED IDEA:\n{improved}"
    )
    return judge.invoke(prompt, config={"run_name": "verifier", "tags": ["verification-loop"]})
