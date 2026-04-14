import json
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path("data/execution_node_registry.json")


def load_execution_node_registry(registry_path: Path | str = REGISTRY_PATH) -> list[dict[str, Any]]:
    path = Path(registry_path)
    with path.open("r", encoding="utf-8") as file:
        entries = json.load(file)

    if not isinstance(entries, list):
        raise ValueError("execution node registry must be a list")

    return entries


def find_execution_node(target_node: str, registry_path: Path | str = REGISTRY_PATH) -> dict[str, Any] | None:
    for entry in load_execution_node_registry(registry_path):
        if entry.get("node") == target_node:
            return entry
    return None


def build_execution_output(
    target_node: str,
    entry: dict[str, Any] | None,
    *,
    execution_type: str,
    definition: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output = {
        "node": target_node,
        "execution_type": execution_type,
        "definition": definition if definition is not None else "",
        "formula": "",
        "causal_relations": [],
    }

    if entry is not None:
        output["definition"] = definition if definition is not None else entry.get("definition", "")
        output["formula"] = entry.get("formula", "")
        output["causal_relations"] = entry.get("causal_relations", [])

    if extra:
        output.update(extra)

    return output
