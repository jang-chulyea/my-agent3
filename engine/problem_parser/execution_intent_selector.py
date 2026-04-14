INTENT_CONCEPT_EXPLANATION = "concept_explanation"
INTENT_CALCULATION = "calculation"
INTENT_JUDGEMENT = "judgement"
INTENT_UNKNOWN = "unknown"


INTENT_KEYWORDS = {
    INTENT_CONCEPT_EXPLANATION: ("정의", "무엇", "의미"),
    INTENT_CALCULATION: ("계산", "구하라", "값", "얼마"),
    INTENT_JUDGEMENT: ("가능", "불가능", "옳은가", "판단"),
}


def select_execution_intent(problem_text: str) -> str:
    normalized_text = problem_text.strip().lower()
    if not normalized_text:
        return INTENT_UNKNOWN

    matched_intents = [
        intent
        for intent, keywords in INTENT_KEYWORDS.items()
        if any(keyword in normalized_text for keyword in keywords)
    ]

    if len(matched_intents) == 1:
        return matched_intents[0]

    return INTENT_UNKNOWN
