from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RegistryEntry:
    canonical_name: str
    aliases: List[str]
    related_nodes: List[str]


@dataclass(frozen=True)
class MatchedTerm:
    text: str
    mapped_to: str
    score: float


@dataclass(frozen=True)
class MappingResult:
    target_node: str
    related_nodes: List[str]
    matched_terms: List[MatchedTerm]
    confidence: float
    score_breakdown: Dict[str, float]
    selection_reasons: List[str]
