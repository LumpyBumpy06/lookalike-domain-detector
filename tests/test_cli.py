import json
import logging
import subprocess
import sys
from pathlib import Path

import pytest

from lookalike.cli import main

EXIT_SUCCESS = 0
EXIT_USAGE_ERROR = 2


def write_input_file(path: Path, contents: str) -> Path:
    """Write UTF-8 test input to ``path`` and return the path."""
    path.write_text(contents, encoding="utf-8")
    return path


def test_main_outputs_text_findings(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() renders findings in deterministic human-readable form."""
    brands = write_input_file(
        tmp_path / "brands.txt",
        "paypal.com\n",
    )
    candidates = write_input_file(
        tmp_path / "candidates.txt",
        "paypall.com\npaypal.net\npaypal-secure.com\nlogin.paypal.com\n",
    )

    exit_code = main(
        [
            "--brands",
            str(brands),
            "--candidates",
            str(candidates),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_SUCCESS
    assert captured.out == (
        "paypal-secure.com -> paypal.com [brand_token]\n"
        "paypal.net -> paypal.com [suffix_swap]\n"
        "paypall.com -> paypal.com [typosquat]\n"
    )
    assert captured.err == ""


def test_main_outputs_json_findings(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() renders findings as a JSON array."""
    brands = write_input_file(
        tmp_path / "brands.txt",
        "paypal.com\n",
    )
    candidates = write_input_file(
        tmp_path / "candidates.txt",
        "paypall.com\npaypal.net\n",
    )

    exit_code = main(
        [
            "--brands",
            str(brands),
            "--candidates",
            str(candidates),
            "--format",
            "json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_SUCCESS
    assert captured.err == ""

    assert json.loads(captured.out) == [
        {
            "candidate": "paypal.net",
            "brand": "paypal.com",
            "detectors": ["suffix_swap"],
        },
        {
            "candidate": "paypall.com",
            "brand": "paypal.com",
            "detectors": ["typosquat"],
        },
    ]


def test_main_reports_skipped_invalid_lines(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """main() logs skipped invalid input lines without failing the run."""
    caplog.set_level(logging.WARNING)

    brands = write_input_file(
        tmp_path / "brands.txt",
        "paypal.com\nnot-a-domain\n",
    )
    candidates = write_input_file(
        tmp_path / "candidates.txt",
        "paypall.com\n.invalid.com\n\n# comment\n",
    )

    exit_code = main(
        [
            "--brands",
            str(brands),
            "--candidates",
            str(candidates),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_SUCCESS
    assert captured.out == "paypall.com -> paypal.com [typosquat]\n"
    assert captured.err == ""

    assert "brands: skipped 1 unsupported or malformed domain line" in caplog.text
    assert "candidates: skipped 1 unsupported or malformed domain line" in caplog.text


def test_main_returns_usage_error_when_brands_file_is_missing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """main() returns the usage error code when the brands file is missing."""
    caplog.set_level(logging.ERROR)

    candidates = write_input_file(
        tmp_path / "candidates.txt",
        "paypall.com\n",
    )
    missing_brands = tmp_path / "missing-brands.txt"

    exit_code = main(
        [
            "--brands",
            str(missing_brands),
            "--candidates",
            str(candidates),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_USAGE_ERROR
    assert captured.out == ""
    assert captured.err == ""
    assert str(missing_brands) in caplog.text


def test_main_returns_usage_error_when_candidates_file_is_missing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """main() returns the usage error code when the candidates file is missing."""
    caplog.set_level(logging.ERROR)

    brands = write_input_file(
        tmp_path / "brands.txt",
        "paypal.com\n",
    )
    missing_candidates = tmp_path / "missing-candidates.txt"

    exit_code = main(
        [
            "--brands",
            str(brands),
            "--candidates",
            str(missing_candidates),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_USAGE_ERROR
    assert captured.out == ""
    assert captured.err == ""
    assert str(missing_candidates) in caplog.text


def test_main_returns_usage_error_for_invalid_format(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() returns the usage error code for an unsupported format."""
    brands = write_input_file(
        tmp_path / "brands.txt",
        "paypal.com\n",
    )
    candidates = write_input_file(
        tmp_path / "candidates.txt",
        "paypall.com\n",
    )

    exit_code = main(
        [
            "--brands",
            str(brands),
            "--candidates",
            str(candidates),
            "--format",
            "xml",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_USAGE_ERROR
    assert captured.out == ""
    assert "invalid choice" in captured.err
    assert "xml" in captured.err


def test_main_returns_usage_error_for_missing_required_argument(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() returns the usage error code when a required argument is missing."""
    exit_code = main(["--brands", "brands.txt"])

    captured = capsys.readouterr()

    assert exit_code == EXIT_USAGE_ERROR
    assert captured.out == ""
    assert "--candidates" in captured.err


def test_main_help_returns_success(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() handles --help without propagating argparse's SystemExit."""
    exit_code = main(["--help"])

    captured = capsys.readouterr()

    assert exit_code == EXIT_SUCCESS
    assert captured.err == ""
    assert "usage:" in captured.out
    assert "--brands" in captured.out
    assert "--candidates" in captured.out
    assert "--format" in captured.out


def test_python_module_entry_point_works(
    tmp_path: Path,
) -> None:
    """The package can be invoked through ``python -m lookalike``."""
    brands = write_input_file(
        tmp_path / "brands.txt",
        "paypal.com\n",
    )
    candidates = write_input_file(
        tmp_path / "candidates.txt",
        "paypall.com\n",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "lookalike",
            "--brands",
            str(brands),
            "--candidates",
            str(candidates),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == EXIT_SUCCESS
    assert result.stdout == "paypall.com -> paypal.com [typosquat]\n"
    assert result.stderr == ""


def test_main_returns_usage_error_for_non_utf8_input(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """main() returns the usage error code when an input file is not UTF-8."""
    caplog.set_level(logging.ERROR)

    brands = write_input_file(
        tmp_path / "brands.txt",
        "paypal.com\n",
    )
    candidates = tmp_path / "candidates.txt"
    candidates.write_bytes(b"paypall.com\n\xe9\n")

    exit_code = main(
        [
            "--brands",
            str(brands),
            "--candidates",
            str(candidates),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_USAGE_ERROR
    assert captured.out == ""
    assert captured.err == ""
    assert str(candidates) in caplog.text


def test_main_returns_usage_error_for_empty_brands_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """main() returns the usage error code when no brands are provided."""
    caplog.set_level(logging.ERROR)

    brands = write_input_file(
        tmp_path / "brands.txt",
        "",
    )
    candidates = write_input_file(
        tmp_path / "candidates.txt",
        "paypall.com\n",
    )

    exit_code = main(
        [
            "--brands",
            str(brands),
            "--candidates",
            str(candidates),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_USAGE_ERROR
    assert captured.out == ""
    assert captured.err == ""
    assert "brands file contains no valid domains" in caplog.text


def test_main_returns_usage_error_when_brands_file_has_no_valid_domains(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """main() rejects a brands file containing no valid domain entries."""
    caplog.set_level(logging.ERROR)

    brands = write_input_file(
        tmp_path / "brands.txt",
        "# protected brands\n\nnot-a-domain\n",
    )
    candidates = write_input_file(
        tmp_path / "candidates.txt",
        "paypall.com\n",
    )

    exit_code = main(
        [
            "--brands",
            str(brands),
            "--candidates",
            str(candidates),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == EXIT_USAGE_ERROR
    assert captured.out == ""
    assert captured.err == ""
    assert "brands file contains no valid domains" in caplog.text
