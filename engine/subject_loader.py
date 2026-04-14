import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SubjectLoaderService:
    """Service skeleton for subject loading responsibilities.

    TODO:
    - Move structured loading logic here from `tools/simple_subject_loader.py`
      only after behavior is protected by tests.
    - Keep this service focused on reading and validating subject data.
    - Do not place CLI formatting or printing logic here.
    """

    def __init__(self, subject_root: str):
        # Loading state is initialized here, but disk I/O is still deferred until
        # explicit load methods are called.
        self.subject_root = Path(subject_root)
        self.subject_meta: Dict[str, Any] = {}
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.prerequisite_edges: List[Dict[str, Any]] = []

    def load_subject(self) -> None:
        self.subject_meta = self.load_subject_meta()
        self.nodes = self.load_nodes()
        self.prerequisite_edges = self.load_prerequisite_edges()

    def load_subject_meta(self) -> Dict[str, Any]:
        subject_file = self.subject_root / "subject.json"
        if not subject_file.exists():
            raise FileNotFoundError(f"subject.json not found: {subject_file}")

        with subject_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        required_fields = ["subject_id", "title", "node_folder", "relation_folder"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field in subject.json: {field}")

        return data

    def load_nodes(self) -> Dict[str, Dict[str, Any]]:
        node_folder_name = self.subject_meta["node_folder"]
        node_dir = self.subject_root / node_folder_name

        if not node_dir.exists():
            raise FileNotFoundError(f"Node folder not found: {node_dir}")

        node_map: Dict[str, Dict[str, Any]] = {}

        for file_path in node_dir.glob("*.json"):
            with file_path.open("r", encoding="utf-8") as file:
                node_data = json.load(file)

            node_id = node_data.get("node_id")
            if not node_id:
                raise ValueError(f"Missing node_id in file: {file_path.name}")

            node_map[node_id] = node_data

        return node_map

    def load_prerequisite_edges(self) -> List[Dict[str, Any]]:
        relation_folder_name = self.subject_meta["relation_folder"]
        relation_dir = self.subject_root / relation_folder_name
        edge_file = relation_dir / "prerequisite_edges.json"

        if not edge_file.exists():
            return []

        with edge_file.open("r", encoding="utf-8") as file:
            edges = json.load(file)

        if not isinstance(edges, list):
            raise ValueError("prerequisite_edges.json must contain a list")

        return edges

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(node_id)

    def get_node_ids(self) -> List[str]:
        return sorted(self.nodes.keys())

    def get_prerequisite_node_ids(self, target_node_id: str) -> List[str]:
        # TODO:
        # - Resolve prerequisite node IDs for a target node.
        # - Keep traversal rules simple for MVP; no graph engine should be added yet.
        raise NotImplementedError

    def get_prerequisite_nodes(self, target_node_id: str) -> List[Dict[str, Any]]:
        # TODO:
        # - Materialize prerequisite node payloads from prerequisite IDs.
        # - Later consider whether this responsibility should stay here or move to
        #   a dedicated bundle/query service.
        raise NotImplementedError

    def get_learning_bundle(self, target_node_id: str) -> Dict[str, Any]:
        # TODO:
        # - This method is a temporary placeholder because the current tools-based
        #   loader exposes bundle creation directly.
        # - Long term, bundle assembly may move to a separate engine service
        #   such as `bundle_service.py`.
        # - Keep the current signature in mind to preserve migration safety.
        raise NotImplementedError
