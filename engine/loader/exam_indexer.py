GROUPED_PROBLEMS = {}


def group_by_minor_subject(problems):
    grouped = {}

    for problem in problems:
        minor_subject = problem.get("minor_subject", "")
        grouped.setdefault(minor_subject, []).append(problem)

    global GROUPED_PROBLEMS
    GROUPED_PROBLEMS = grouped

    return grouped


def get_problems_by_subject(subject):
    return GROUPED_PROBLEMS.get(subject, [])


def list_minor_subjects():
    return list(GROUPED_PROBLEMS.keys())


def get_subject_problem_map():
    return GROUPED_PROBLEMS


def get_problems_by_tag(tag):
    matched = []

    for problems in GROUPED_PROBLEMS.values():
        for problem in problems:
            if tag in problem.get("tags", []):
                matched.append(problem)

    return matched
