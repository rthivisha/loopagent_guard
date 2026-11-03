from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import ModelCallLimitMiddleware

load_dotenv(override=True)

MODEL = "google_genai:gemini-2.5-flash"
WORKSPACE = "workspace"


def build_agent(max_calls: int = 3):
    backend = FilesystemBackend(root_dir=WORKSPACE, virtual_mode=True)
    return create_deep_agent(
        model=MODEL,
        system_prompt="Your instructions are in /memories/AGENTS.md.",
        backend=backend,
        memory=["/memories/AGENTS.md"],
        skills=["/skills/"],
        middleware=[ModelCallLimitMiddleware(run_limit=max_calls, exit_behavior="end")],
    )
