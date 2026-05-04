import json
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FREQUENCY_SCRIPT = PROJECT_ROOT / "tools" / "calculate_topic_frequency.py"
IMPORTANCE_SCRIPT = PROJECT_ROOT / "tools" / "calculate_topic_importance.py"


@contextmanager
def make_workspace_tmpdir() -> Path:
    base_dir = PROJECT_ROOT / ".pytest_local_tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="topic-analytics-", dir=base_dir))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_calculate_topic_frequency_and_importance_cli() -> None:
    with make_workspace_tmpdir() as tmp_path:
        exam_path = (
            tmp_path
            / "data"
            / "exams"
            / "ac_refrigeration_engineer"
            / "2024_1"
            / "exam_2024_1.json"
        )
        analytics_root = tmp_path / "data" / "analytics"
        exam_path.parent.mkdir(parents=True)

        exam_payload = {
            "exam_info": {"title": "Sample Exam"},
            "problems": [
                {"problem_id": "p1", "topic": "thermodynamics"},
                {"problem_id": "p2", "topic": "thermodynamics"},
                {"problem_id": "p3", "topic": "refrigeration_cycle"},
                {"problem_id": "p4", "topic": "expansion_valve"},
                {"problem_id": "p5", "topic": ""},
                {"problem_id": "p6"},
            ],
        }
        exam_path.write_text(
            json.dumps(exam_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        frequency_output = analytics_root / "topic_frequency.json"
        importance_output = analytics_root / "topic_importance.json"

        frequency_run = subprocess.run(
            [
                sys.executable,
                str(FREQUENCY_SCRIPT),
                "--input",
                str(exam_path),
                "--output",
                str(frequency_output),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        assert frequency_output.exists()
        assert "Saved topic frequency analytics to:" in frequency_run.stdout

        frequency_payload = json.loads(frequency_output.read_text(encoding="utf-8"))
        assert frequency_payload["summary"]["input_file"] == str(exam_path)
        assert frequency_payload["summary"]["processed_files"] == 1
        assert frequency_payload["summary"]["processed_problems"] == 6
        assert frequency_payload["summary"]["skipped_problems"] == 2
        assert frequency_payload["summary"]["counted_topics"] == 4
        assert frequency_payload["summary"]["unique_topics"] == 3
        assert frequency_payload["topics"] == [
            {"topic": "thermodynamics", "frequency": 2},
            {"topic": "expansion_valve", "frequency": 1},
            {"topic": "refrigeration_cycle", "frequency": 1},
        ]

        importance_run = subprocess.run(
            [
                sys.executable,
                str(IMPORTANCE_SCRIPT),
                "--input",
                str(frequency_output),
                "--output",
                str(importance_output),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        assert importance_output.exists()
        assert "Saved topic importance analytics to:" in importance_run.stdout

        importance_payload = json.loads(importance_output.read_text(encoding="utf-8"))
        assert importance_payload["summary"]["unique_topics"] == 3
        assert importance_payload["topics"] == [
            {
                "topic": "thermodynamics",
                "frequency": 2,
                "importance": 2,
                "label": "normal",
            },
            {
                "topic": "expansion_valve",
                "frequency": 1,
                "importance": 1,
                "label": "normal",
            },
            {
                "topic": "refrigeration_cycle",
                "frequency": 1,
                "importance": 1,
                "label": "normal",
            },
        ]


def test_importance_labels_follow_phase_1_thresholds() -> None:
    with make_workspace_tmpdir() as tmp_path:
        analytics_root = tmp_path / "data" / "analytics"
        analytics_root.mkdir(parents=True)

        frequency_payload = {
            "summary": {"unique_topics": 3},
            "topics": [
                {"topic": "topic_a", "frequency": 10},
                {"topic": "topic_b", "frequency": 5},
                {"topic": "topic_c", "frequency": 4},
            ],
        }
        frequency_output = analytics_root / "topic_frequency.json"
        importance_output = analytics_root / "topic_importance.json"
        frequency_output.write_text(
            json.dumps(frequency_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        subprocess.run(
            [
                sys.executable,
                str(IMPORTANCE_SCRIPT),
                "--input",
                str(frequency_output),
                "--output",
                str(importance_output),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        importance_payload = json.loads(importance_output.read_text(encoding="utf-8"))
        assert importance_payload["topics"] == [
            {
                "topic": "topic_a",
                "frequency": 10,
                "importance": 10,
                "label": "very_important",
            },
            {
                "topic": "topic_b",
                "frequency": 5,
                "importance": 5,
                "label": "important",
            },
            {
                "topic": "topic_c",
                "frequency": 4,
                "importance": 4,
                "label": "normal",
            },
        ]
