import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SubjectLoader:
    def __init__(self, subject_root: str):
        self.subject_root = Path(subject_root)
        self.subject_meta: Dict[str, Any] = {}
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.prerequisite_edges: List[Dict[str, Any]] = []

    def load_subject(self) -> None:
        self.subject_meta = self._load_subject_meta()
        self.nodes = self._load_nodes()
        self.prerequisite_edges = self._load_prerequisite_edges()

    def _load_subject_meta(self) -> Dict[str, Any]:
        subject_file = self.subject_root / "subject.json"
        if not subject_file.exists():
            raise FileNotFoundError(f"subject.json not found: {subject_file}")

        with subject_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        required_fields = ["subject_id", "title", "node_folder", "relation_folder"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field in subject.json: {field}")

        return data

    def _load_nodes(self) -> Dict[str, Dict[str, Any]]:
        node_folder_name = self.subject_meta["node_folder"]
        node_dir = self.subject_root / node_folder_name

        if not node_dir.exists():
            raise FileNotFoundError(f"Node folder not found: {node_dir}")

        node_map: Dict[str, Dict[str, Any]] = {}

        for file_path in node_dir.glob("*.json"):
            with file_path.open("r", encoding="utf-8") as f:
                node_data = json.load(f)

            node_id = node_data.get("node_id")
            if not node_id:
                raise ValueError(f"Missing node_id in file: {file_path.name}")

            node_map[node_id] = node_data

        return node_map

    def _load_prerequisite_edges(self) -> List[Dict[str, Any]]:
        relation_folder_name = self.subject_meta["relation_folder"]
        relation_dir = self.subject_root / relation_folder_name
        edge_file = relation_dir / "prerequisite_edges.json"

        if not edge_file.exists():
            return []

        with edge_file.open("r", encoding="utf-8") as f:
            edges = json.load(f)

        if not isinstance(edges, list):
            raise ValueError("prerequisite_edges.json must contain a list")

        return edges

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(node_id)

    def get_prerequisite_node_ids(self, target_node_id: str) -> List[str]:
        results: List[str] = []

        for edge in self.prerequisite_edges:
            if (
                edge.get("target_node_id") == target_node_id
                and edge.get("relation") == "prerequisite"
            ):
                source_node_id = edge.get("source_node_id")
                if source_node_id:
                    results.append(source_node_id)

        return results

    def get_prerequisite_nodes(self, target_node_id: str) -> List[Dict[str, Any]]:
        prerequisite_ids = self.get_prerequisite_node_ids(target_node_id)
        results: List[Dict[str, Any]] = []

        for node_id in prerequisite_ids:
            node = self.get_node(node_id)
            if node:
                results.append(node)

        return results

    def get_learning_bundle(self, target_node_id: str) -> Dict[str, Any]:
        target_node = self.get_node(target_node_id)
        if not target_node:
            raise ValueError(f"Target node not found: {target_node_id}")

        prerequisites = self.get_prerequisite_nodes(target_node_id)

        return {
            "subject": {
                "subject_id": self.subject_meta.get("subject_id"),
                "title": self.subject_meta.get("title"),
            },
            "target_node": target_node,
            "prerequisite_nodes": prerequisites,
        }


def print_learning_bundle(bundle: Dict[str, Any]) -> None:
    subject = bundle["subject"]
    target_node = bundle["target_node"]
    prerequisite_nodes = bundle["prerequisite_nodes"]

    print("=" * 60)
    print(f"[과목] {subject['title']} ({subject['subject_id']})")
    print(f"[현재 개념] {target_node['title']} ({target_node['node_id']})")
    print("-" * 60)

    short_def = target_node.get("definition", {}).get("short", "")
    print(f"정의: {short_def}")

    level1 = target_node.get("level_content", {}).get("level_1_intuition", {}).get("content", "")
    level2 = target_node.get("level_content", {}).get("level_2_principle", {}).get("content", "")
    
    print("\n[Level 1]")
    print(level1)
    
    print("\n[Level 2]")
    print(level2)

    print("\n[먼저 알아야 할 개념]")
    if not prerequisite_nodes:
        print("- 없음")
    else:
        for idx, node in enumerate(prerequisite_nodes, start=1):
            node_title = node.get("title", "Untitled")
            node_id = node.get("node_id", "Unknown")
            node_def = node.get("definition", {}).get("short", "")
            print(f"{idx}. {node_title} ({node_id})")
            print(f"   - {node_def}")

    print("=" * 60)


if __name__ == "__main__":
    subject_path = "data/subject_02_hvac"

    loader = SubjectLoader(subject_path)
    loader.load_subject()

    bundle = loader.get_learning_bundle("TD-01-PRESSURE")
    print_learning_bundle(bundle)
    