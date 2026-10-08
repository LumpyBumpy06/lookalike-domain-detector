"""Detectors: each detector decides whether a candidate imitates one brand in one way"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    """A detector's result on one (candidate, brand) pair with its confidence score."""

    detector: str
    score: float
