"""Command-line interface for the lookalike domain detector."""

import argparse
import json
import logging
from collections.abc import Sequence
from pathlib import Path

from lookalike.detection import Finding
from lookalike.detectors.factory import default_detectors
from lookalike.inputs import InputParseResult, parse_domain_lines
from lookalike.pipeline import run_pipeline

EXIT_SUCCESS = 0
EXIT_USAGE_ERROR = 2

DEFAULT_OUTPUT_FORMAT = "text"
OUTPUT_FORMATS = ("text", "json")

LOGGER = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line application and return its process exit code."""
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return _system_exit_code(exc)

    return _run(args.brands, args.candidates, args.format)


def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="lookalike",
        description="Detect domains that resemble protected brands.",
    )
    parser.add_argument(
        "--brands",
        required=True,
        type=Path,
        help="Path to the file containing protected brand domains.",
    )
    parser.add_argument(
        "--candidates",
        required=True,
        type=Path,
        help="Path to the file containing candidate domains.",
    )
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help="Output format (default: %(default)s).",
    )
    return parser


def _run(
    brands_path: Path,
    candidates_path: Path,
    output_format: str,
) -> int:
    """Load inputs, analyse domains and render the results."""
    brands_result = _read_input_file(brands_path, "brands")
    if brands_result is None:
        return EXIT_USAGE_ERROR

    candidates_result = _read_input_file(candidates_path, "candidates")
    if candidates_result is None:
        return EXIT_USAGE_ERROR

    _report_skipped("brands", brands_result)
    _report_skipped("candidates", candidates_result)

    findings = run_pipeline(
        candidates=candidates_result.domains,
        brands=brands_result.domains,
        detectors=default_detectors(),
    )

    _write_output(findings, output_format)
    return EXIT_SUCCESS


def _read_input_file(
    path: Path,
    source_name: str,
) -> InputParseResult | None:
    """Read and parse one domain input file, logging read failures."""
    try:
        return _read_domains(path)
    except OSError as exc:
        LOGGER.error(
            "unable to read %s file %s: %s",
            source_name,
            path,
            exc.strerror or exc,
        )
        return None


def _read_domains(path: Path) -> InputParseResult:
    """Read and parse domain lines from ``path``."""
    with path.open("r", encoding="utf-8") as file:
        return parse_domain_lines(file)


def _report_skipped(source_name: str, result: InputParseResult) -> None:
    """Log the number of invalid input lines skipped from one source."""
    if result.skipped:
        LOGGER.warning(
            "%s: skipped %d invalid line%s",
            source_name,
            result.skipped,
            "" if result.skipped == 1 else "s",
        )


def _write_output(
    findings: tuple[Finding, ...],
    output_format: str,
) -> None:
    """Render findings to standard output."""
    if output_format == "json":
        _write_json(findings)
        return

    _write_text(findings)


def _write_text(findings: tuple[Finding, ...]) -> None:
    """Write findings in a human-readable line-oriented format."""
    for finding in findings:
        detector_names = ", ".join(detection.detector for detection in finding.detections)
        print(f"{finding.candidate.full} -> {finding.brand.full} [{detector_names}]")


def _write_json(findings: tuple[Finding, ...]) -> None:
    """Write findings as a JSON array."""
    payload = [
        {
            "candidate": finding.candidate.full,
            "brand": finding.brand.full,
            "detectors": [detection.detector for detection in finding.detections],
        }
        for finding in findings
    ]

    print(json.dumps(payload, indent=2))


def _system_exit_code(exc: SystemExit) -> int:
    """Convert argparse's SystemExit into an integer return value."""
    if isinstance(exc.code, int):
        return exc.code

    return EXIT_USAGE_ERROR
