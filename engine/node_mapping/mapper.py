import json
from collections import Counter
from pathlib import Path

from engine.node_mapping.extractor import extract_candidate_terms
from engine.node_mapping.normalizer import normalize_text, normalize_token
from engine.node_mapping.schemas import MappingResult, MatchedTerm, RegistryEntry


DEFAULT_REGISTRY_PATH = Path("data/node_registry.json")
QUESTION_FOCUS_MARKERS = [
    "무엇",
    "왜",
    "어떻게",
    "정의",
    "의미",
    "영향",
    "변하",
    "변화",
    "얼마",
    "달라지",
    "계산",
]
TOPIC_SUFFIXES = ["은", "는", "이", "가", "을", "를", "에"]
MIXED_TARGET_NODES = {"pressure", "force", "area"}
PRIMARY_TARGET_SUFFIXES = {"은", "는", "을", "를", "에"}
SECONDARY_TARGET_SUFFIXES = {"이", "가"}


def load_node_registry(registry_path: str | Path = DEFAULT_REGISTRY_PATH) -> list[RegistryEntry]:
    path = Path(registry_path)
    with path.open("r", encoding="utf-8") as file:
        raw_entries = json.load(file)

    return [
        RegistryEntry(
            canonical_name=entry["canonical_name"],
            aliases=entry["aliases"],
            related_nodes=entry.get("related_nodes", []),
        )
        for entry in raw_entries
    ]


def _find_positions(text: str, needle: str) -> list[int]:
    positions: list[int] = []
    start = 0
    while True:
        index = text.find(needle, start)
        if index < 0:
            return positions
        positions.append(index)
        start = index + 1


def _compute_focus_bonus(aliases: list[str], normalized_problem_text: str) -> tuple[float, list[str]]:
    marker_positions = [
        position
        for marker in QUESTION_FOCUS_MARKERS
        for position in _find_positions(normalized_problem_text, marker)
    ]
    if not marker_positions:
        return 0.0, []

    best_bonus = 0.0
    reasons: list[str] = []

    for alias in aliases:
        normalized_alias = normalize_text(alias)
        if not normalized_alias:
            continue

        alias_positions = _find_positions(normalized_problem_text, normalized_alias)
        for alias_position in alias_positions:
            nearest_distance = min(abs(marker_position - alias_position) for marker_position in marker_positions)
            proximity_bonus = max(0.0, 1.2 - (nearest_distance * 0.08))
            if proximity_bonus > best_bonus:
                best_bonus = proximity_bonus
                reasons = [f"focus proximity bonus {round(proximity_bonus, 3)} via {alias}"]

            for suffix in TOPIC_SUFFIXES:
                pattern = f"{normalized_alias}{suffix}"
                pattern_position = normalized_problem_text.find(pattern)
                if pattern_position < 0:
                    continue
                nearest_distance = min(abs(marker_position - pattern_position) for marker_position in marker_positions)
                if suffix in PRIMARY_TARGET_SUFFIXES:
                    asked_bonus = max(0.0, 1.6 - (nearest_distance * 0.09))
                else:
                    asked_bonus = max(0.0, 0.55 - (nearest_distance * 0.06))
                if asked_bonus > best_bonus:
                    best_bonus = asked_bonus
                    reasons = [f"asked-about bonus {round(asked_bonus, 3)} via {pattern}"]

    return round(best_bonus, 3), reasons


def _compute_explicit_target_bonus(aliases: list[str], normalized_problem_text: str) -> tuple[float, list[str]]:
    best_bonus = 0.0
    reasons: list[str] = []

    for alias in aliases:
        normalized_alias = normalize_text(alias)
        if not normalized_alias:
            continue

        for suffix in TOPIC_SUFFIXES:
            pattern = f"{normalized_alias}{suffix}"
            pattern_position = normalized_problem_text.find(pattern)
            if pattern_position < 0:
                continue

            trailing_text = normalized_problem_text[pattern_position : pattern_position + 24]
            if any(marker in trailing_text for marker in QUESTION_FOCUS_MARKERS):
                if suffix in PRIMARY_TARGET_SUFFIXES and 2.1 > best_bonus:
                    best_bonus = 2.1
                    reasons = [f"explicit asked-target bonus 2.1 via {pattern}"]
                elif suffix in SECONDARY_TARGET_SUFFIXES and 0.35 > best_bonus:
                    best_bonus = 0.35
                    reasons = [f"secondary topic bonus 0.35 via {pattern}"]
            elif "영향" in normalized_problem_text and suffix == "에":
                if 2.4 > best_bonus:
                    best_bonus = 2.4
                    reasons = [f"influence target bonus 2.4 via {pattern}"]

    return round(best_bonus, 3), reasons


def map_problem_to_nodes(
    problem_text: str,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> MappingResult:
    registry = load_node_registry(registry_path)
    candidates = extract_candidate_terms(problem_text)
    normalized_problem_text = normalize_text(problem_text)
    normalized_candidates = [normalize_text(candidate) for candidate in candidates]
    candidate_counter = Counter(normalized_candidates)
    first_position_by_candidate = {
        candidate: index for index, candidate in enumerate(normalized_candidates)
    }

    matched_terms: list[MatchedTerm] = []
    score_by_node: dict[str, float] = {}
    related_nodes_by_node: dict[str, list[str]] = {}
    reasons_by_node: dict[str, list[str]] = {}
    aliases_by_node: dict[str, list[str]] = {}

    for entry in registry:
        node_total_score = 0.0
        node_matches: list[MatchedTerm] = []
        node_reasons: list[str] = []
        aliases_by_node[entry.canonical_name] = entry.aliases

        for alias in entry.aliases:
            normalized_alias = normalize_text(alias)
            normalized_alias_token = normalize_token(normalized_alias)
            if not normalized_alias:
                continue

            alias_score = 0.0
            reasons: list[str] = []

            if normalized_alias in candidate_counter:
                alias_score += 1.4
                reasons.append("exact candidate match")

            if normalized_alias_token in candidate_counter and normalized_alias_token != normalized_alias:
                alias_score += 1.1
                reasons.append("normalized token match")

            partial_hits = [
                candidate
                for candidate in normalized_candidates
                if normalized_alias in candidate or candidate in normalized_alias
            ]
            if partial_hits:
                alias_score += 0.6
                reasons.append("partial match")

            if normalized_alias in normalized_problem_text:
                alias_score += 0.4
                reasons.append("substring in problem text")

            if alias_score == 0.0:
                continue

            occurrence_count = candidate_counter.get(normalized_alias, 0) + candidate_counter.get(
                normalized_alias_token,
                0,
            )
            if occurrence_count:
                repeat_bonus = min(0.4, occurrence_count * 0.15)
                alias_score += repeat_bonus
                reasons.append(f"repeat bonus {round(repeat_bonus, 3)}")

            candidate_positions = [
                first_position_by_candidate[key]
                for key in {normalized_alias, normalized_alias_token}
                if key in first_position_by_candidate
            ]
            if candidate_positions:
                first_position = min(candidate_positions)
                first_bonus = max(0.0, 0.4 - (first_position * 0.08))
                alias_score += first_bonus
                reasons.append(f"first appearance bonus {round(first_bonus, 3)}")

            alias_score = round(alias_score, 3)
            node_total_score += alias_score
            node_matches.append(
                MatchedTerm(
                    text=alias,
                    mapped_to=entry.canonical_name,
                    score=alias_score,
                )
            )
            node_reasons.append(f"{alias}: {', '.join(reasons)}")

        if not node_matches:
            continue

        score_by_node[entry.canonical_name] = round(
            score_by_node.get(entry.canonical_name, 0.0) + node_total_score,
            3,
        )
        related_nodes_by_node[entry.canonical_name] = entry.related_nodes
        reasons_by_node[entry.canonical_name] = node_reasons
        matched_terms.extend(node_matches)

    if not score_by_node:
        return MappingResult(
            target_node="",
            related_nodes=[],
            matched_terms=[],
            confidence=0.0,
            score_breakdown={},
            selection_reasons=[],
        )

    matched_node_names = set(score_by_node)
    if MIXED_TARGET_NODES.issubset(matched_node_names):
        for node_name in MIXED_TARGET_NODES:
            focus_bonus, focus_reasons = _compute_focus_bonus(
                aliases_by_node[node_name],
                normalized_problem_text,
            )
            if focus_bonus > 0.0:
                score_by_node[node_name] = round(score_by_node[node_name] + focus_bonus, 3)
                reasons_by_node[node_name].extend(focus_reasons)

            explicit_bonus, explicit_reasons = _compute_explicit_target_bonus(
                aliases_by_node[node_name],
                normalized_problem_text,
            )
            if explicit_bonus > 0.0:
                score_by_node[node_name] = round(score_by_node[node_name] + explicit_bonus, 3)
                reasons_by_node[node_name].extend(explicit_reasons)

            if "영향" in normalized_problem_text:
                influence_patterns = [
                    f"{normalize_text(alias)}에"
                    for alias in aliases_by_node[node_name]
                    if normalize_text(alias)
                ]
                if any(pattern in normalized_problem_text for pattern in influence_patterns):
                    score_by_node[node_name] = round(score_by_node[node_name] + 2.6, 3)
                    reasons_by_node[node_name].append("direct influence-target bonus 2.6")

    sorted_nodes = sorted(
        score_by_node.items(),
        key=lambda item: (item[1], len(item[0])),
        reverse=True,
    )
    target_node = sorted_nodes[0][0]
    target_score = sorted_nodes[0][1]
    runner_up_score = sorted_nodes[1][1] if len(sorted_nodes) > 1 else 0.0
    competition_penalty = min(0.45, max(0.0, runner_up_score / max(target_score, 0.001)) * 0.35)
    match_volume_bonus = min(0.25, len([m for m in matched_terms if m.mapped_to == target_node]) * 0.08)
    base_confidence = min(1.0, target_score / 2.2)
    confidence = max(0.0, min(1.0, round(base_confidence + match_volume_bonus - competition_penalty, 3)))

    return MappingResult(
        target_node=target_node,
        related_nodes=related_nodes_by_node.get(target_node, []),
        matched_terms=sorted(matched_terms, key=lambda item: item.score, reverse=True),
        confidence=confidence,
        score_breakdown=score_by_node,
        selection_reasons=reasons_by_node.get(target_node, []),
    )


if __name__ == "__main__":
    result = map_problem_to_nodes("압력이 증가하는 경우는?")
    assert result.target_node == "pressure", result
    print(result)
