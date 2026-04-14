import json
from pathlib import Path
import sys

from engine.execution.dispatcher import dispatch_target_node
from engine.execution.handlers import run_execution_handler
from engine.problem_parser.execution_intent_selector import select_execution_intent
from engine.problem_parser.node_mapping_entry import parse_problem_text


EXAMPLES = [
    "압력의 정의는?",
    "힘이란 무엇인가?",
    "온도가 올라가면 압력은?",
    "효율은 무엇인가?",
    "체적이 줄면 압력은 어떻게 되나?",
]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    for problem_text in EXAMPLES:
        parsed = parse_problem_text(problem_text)
        execution_intent = select_execution_intent(problem_text)
        execution_path = dispatch_target_node(parsed.target_node, execution_intent)
        final_output = run_execution_handler(execution_path, parsed.target_node, problem_text)

        print("=" * 60)
        print("input:", problem_text)
        print("target_node:", parsed.target_node)
        print("execution_intent:", execution_intent)
        print("execution_path:", execution_path)
        print("definition:", final_output.get("definition", ""))
        if final_output.get("formula"):
            print("formula:", final_output.get("formula", ""))
        print("causal_relations:", final_output.get("causal_relations", []))


if __name__ == "__main__":
    main()
