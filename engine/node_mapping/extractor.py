import re
from typing import List

from engine.node_mapping.normalizer import normalize_text, normalize_token


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+|[\uac00-\ud7a3]+")


def extract_candidate_terms(problem_text: str) -> List[str]:
    normalized = normalize_text(problem_text)
    tokens = TOKEN_PATTERN.findall(normalized)

    candidates: list[str] = []
    seen: set[str] = set()

    for token in tokens:
        for candidate in (normalize_token(token), normalize_text(token)):
            if candidate and candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)

    if normalized and normalized not in seen:
        candidates.append(normalized)

    return candidates
