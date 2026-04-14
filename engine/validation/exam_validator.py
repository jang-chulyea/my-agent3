def validate_problem(p):
    required_fields = [
        "module",
        "major_subject",
        "minor_subject",
        "topic",
        "tags",
        "question",
        "answer",
        "explanation"
    ]

    for f in required_fields:
        if f not in p:
            raise ValueError(f"Missing field: {f}")

    return True
