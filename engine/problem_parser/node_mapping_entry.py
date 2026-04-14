from dataclasses import dataclass
import sys

from engine.node_mapping.mapper import map_problem_to_nodes


@dataclass(frozen=True)
class ParsedProblemMapping:
    target_node: str
    related_nodes: list[str]
    confidence: float


def parse_problem_text(problem_text: str) -> ParsedProblemMapping:
    result = map_problem_to_nodes(problem_text)
    return ParsedProblemMapping(
        target_node=result.target_node,
        related_nodes=result.related_nodes,
        confidence=result.confidence,
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    problem_text = " ".join(sys.argv[1:]).strip()
    if not problem_text:
        problem_text = input("problem_text: ").strip()

    parsed = parse_problem_text(problem_text)

    print("target_node:", parsed.target_node)
    print("related_nodes:", parsed.related_nodes)
    print("confidence:", parsed.confidence)


if __name__ == "__main__":
    main()
