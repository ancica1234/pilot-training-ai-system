"""
Aviation Training Multi-Agent System
--------------------------------------
Entry point for running the supervisor graph interactively.

Usage:
    OPENAI_API_KEY=<your-key> python3.11 main.py

The graph will pause before sending any instructor notification and ask
for your confirmation before resuming (human-in-the-loop).
"""

import os

# ── LangSmith Tracing ─────────────────────────────────────────────────────────
# MUST run before importing graph.graph so env vars are set before the LLM
# is instantiated. Every LLM call, tool invocation, and routing decision will
# appear in the LangSmith dashboard at https://smith.langchain.com
def _setup_tracing() -> None:
    api_key = (
        os.environ.get("LANGSMITH_API_KEY") or
        os.environ.get("LANGCHAIN_API_KEY")
    )
    if api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"]     = api_key
        os.environ["LANGSMITH_API_KEY"]     = api_key
        project = os.environ.get("LANGCHAIN_PROJECT", "aviation-training-multi-agent")
        os.environ["LANGCHAIN_PROJECT"]     = project
        try:
            from langsmith import Client
            client = Client(api_key=api_key)
            list(client.list_projects())
            print(f"🔍 LangSmith tracing enabled — project: {project}")
            print(f"   View traces at: https://smith.langchain.com/projects")
        except Exception as e:
            print(f"⚠️  LangSmith connection failed: {e}")
    else:
        print("ℹ️  LangSmith tracing disabled (set LANGSMITH_API_KEY to enable)")

_setup_tracing()  # must be before graph import

from langchain_core.messages import HumanMessage
from graph.graph import graph


def run(query: str) -> None:
    """Stream a query through the graph, handling the instructor_notification interrupt."""
    print("\n" + "=" * 60)
    print(f"QUERY: {query}")
    print("=" * 60)

    config = {"configurable": {"thread_id": "1"}}
    inputs = {"messages": [HumanMessage(content=query)]}

    seen_ids: set = set()

    def print_new_messages(event: dict) -> None:
        """Print only messages we haven't seen before."""
        for msg in event.get("messages", []):
            msg_id = getattr(msg, 'id', id(msg))
            if msg_id in seen_ids:
                continue
            seen_ids.add(msg_id)
            role = msg.__class__.__name__.replace("Message", "")
            content = msg.content
            if content and role not in ("Human", "System"):
                # Truncate very long tool outputs for readability
                display = content if len(content) < 500 else content[:500] + "..."
                print(f"\n[{role}]: {display}")

    while True:
        # Stream events until the graph finishes or hits an interrupt
        try:
            for event in graph.stream(inputs, config=config, stream_mode="values",
                                      recursion_limit=25):
                print_new_messages(event)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate_limit" in err_str.lower():
                import re, time
                wait = 60  # default
                m = re.search(r'try again in (\d+)m([\d.]+)s', err_str)
                if m:
                    wait = int(m.group(1)) * 60 + float(m.group(2)) + 2
                print(f"\n⏳ Rate limit hit. Waiting {wait:.0f}s before retrying...")
                time.sleep(wait)
                continue  # retry the while loop
            import traceback
            print(f"\n❌ Error during graph execution: {e}")
            traceback.print_exc()
            break

        # Check if the graph is interrupted (waiting for human approval)
        state = graph.get_state(config)
        if state.next and "instructor_notification" in state.next:
            print("\n" + "-" * 60)
            print("⚠️  INTERRUPT: Graph is about to send instructor notifications.")
            print("Pending messages:")
            for m in state.values.get("messages", [])[-3:]:
                if m.content:
                    print(f"  {m.__class__.__name__}: {m.content}")
            confirm = input("\nApprove sending notifications? (yes/no): ").strip().lower()
            if confirm == "yes":
                print("✅ Approved — resuming graph...")
                inputs = None  # resume without new input
            else:
                print("❌ Rejected — stopping without sending notifications.")
                break
        else:
            # Graph has fully completed
            break

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


EXAMPLE_QUERIES = [
    "Evaluate John Smith's training progress and assess his risk level.",
    "Compare risk levels for all students in class 25-4.",
    "Build a remediation plan for John Smith, assess his risk, then notify his instructor.",
    "Give me a full status report on class 25-5 and alert the instructor about any high-risk students.",
]


if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable is not set.")
        print("Usage: GROQ_API_KEY=<your-key> python3.11 main.py")
        raise SystemExit(1)

    print("Aviation Training Multi-Agent System")
    print("Available example queries:")
    for i, q in enumerate(EXAMPLE_QUERIES, 1):
        print(f"  {i}. {q}")
    print("  0. Enter a custom query")

    choice = input("\nSelect a query (0-4): ").strip()

    if choice == "0":
        query = input("Enter your query: ").strip()
    elif choice in {"1", "2", "3", "4"}:
        query = EXAMPLE_QUERIES[int(choice) - 1]
    else:
        print("Invalid choice.")
        raise SystemExit(1)

    run(query)
