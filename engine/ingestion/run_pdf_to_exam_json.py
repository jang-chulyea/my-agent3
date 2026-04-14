# PDF-to-exam JSON ingestion scaffold
#
# Stage 1: extract selectable text from the input PDF.
# Stage 2: split extracted text into per-problem blocks.
# Stage 3: normalize each block into the project problem schema.
# Stage 4: validate required fields using the existing exam validator.
# Stage 5: write the final exam JSON payload.

import argparse

from engine.ingestion.exam_json_writer import write_exam_json
from engine.ingestion.pdf_text_extractor import extract_text
from engine.ingestion.problem_block_parser import split_problem_blocks
from engine.ingestion.problem_normalizer import normalize_problem_block


def run_pipeline(input_path: str, output_path: str, module: str) -> dict:
    """Run the selectable-text PDF ingestion pipeline and write exam JSON."""

    raw_text = extract_text(input_path)
    blocks = split_problem_blocks(raw_text)
    problems = [
        normalize_problem_block(block, index, module)
        for index, block in enumerate(blocks, start=1)
    ]
    return write_exam_json(
        problems,
        output_path,
        exam_info={
            "source_file": input_path,
        },
    )


def main() -> None:
    """CLI entrypoint for PDF-to-exam JSON ingestion."""

    parser = argparse.ArgumentParser(description="Convert a selectable-text PDF into exam JSON.")
    parser.add_argument("--input", required=True, help="Input PDF path.")
    parser.add_argument("--output", required=True, help="Output JSON path.")
    parser.add_argument("--module", required=True, help="Problem module value, e.g. exam or core.")
    args = parser.parse_args()

    run_pipeline(args.input, args.output, args.module)


if __name__ == "__main__":
    main()
