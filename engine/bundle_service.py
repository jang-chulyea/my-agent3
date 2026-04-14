from typing import Any, Dict, List


class BundleService:
    """Service skeleton for assembling learning bundles.

    Responsibility boundary:
    - `subject_loader` is responsible for reading and exposing subject data.
    - `bundle_service` is responsible for composing a response structure from
      already loaded subject data.

    TODO:
    - Keep this service focused on bundle assembly and query-style composition.
    - Do not move raw file-reading concerns here.
    - Preserve MVP simplicity; avoid introducing search/recommendation logic here.
    """

    def __init__(self, loader: Any):
        # The bundle service depends on an already-loaded subject loader.
        # For now, the dependency remains intentionally minimal: the loader must
        # expose `subject_meta`, `nodes`, `prerequisite_edges`, and `get_node()`.
        self.loader = loader

    def get_prerequisite_node_ids(self, target_node_id: str) -> List[str]:
        results: List[str] = []

        for edge in self.loader.prerequisite_edges:
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
            node = self.loader.get_node(node_id)
            if node:
                results.append(node)

        return results

    def get_learning_bundle(self, target_node_id: str) -> Dict[str, Any]:
        target_node = self.loader.get_node(target_node_id)
        if not target_node:
            raise ValueError(f"Target node not found: {target_node_id}")

        prerequisites = self.get_prerequisite_nodes(target_node_id)

        return {
            "subject": {
                "subject_id": self.loader.subject_meta.get("subject_id"),
                "title": self.loader.subject_meta.get("title"),
            },
            "target_node": target_node,
            "prerequisite_nodes": prerequisites,
        }

    def build_learning_bundle(self, target_node_id: str) -> Dict[str, Any]:
        # Keep a forward-looking app-facing name while matching the tools-based
        # method contract during migration.
        return self.get_learning_bundle(target_node_id)
