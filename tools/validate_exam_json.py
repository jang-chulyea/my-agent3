import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.validation.exam_validator import validate_exam_payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an exam JSON file.")
    parser.add_argument("path", help="Path to an exam JSON file.")
    args = parser.parse_args()

    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    problems = payload.get("problems", [])
    problem_numbers = [
        problem.get("problem_no")
        for problem in problems
        if isinstance(problem, dict)
    ]
    expected = list(range(1, len(problem_numbers) + 1))

    print(f"path: {args.path}")
    print(f"problem_count: {len(problems) if isinstance(problems, list) else 'invalid'}")
    print(f"sequential: {problem_numbers == expected}")

    try:
        validate_exam_payload(payload)
    except ValueError as exc:
        print(f"validator: failed")
        print(f"error: {exc}")
        raise SystemExit(1)

    print("validator: ok")


if __name__ == "__main__":
    main()
