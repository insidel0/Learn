from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# Constants to avoid "magic numbers"
QUALITY_LAPSE_THRESHOLD = 3
EASE_MIN = 1.3
EASE_START = 2.5
INTERVAL_FIRST = 1
INTERVAL_SECOND = 6


@dataclass
class SRSState:
    interval: int = 0  # days
    ease: float = EASE_START
    reps: int = 0


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def add_days_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).replace(microsecond=0).isoformat()


def review(state: SRSState | None, quality: int) -> tuple[SRSState, str]:
    """
    SM-2 inspired scheduler.
    """
    if state is None:
        state = SRSState()

    ease = state.ease
    reps = state.reps

    if quality < QUALITY_LAPSE_THRESHOLD:
        ease = max(EASE_MIN, ease - 0.2)
        interval = INTERVAL_FIRST
        reps = 0
    else:
        delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        ease = max(EASE_MIN, ease + delta)
        reps += 1
        if state.interval == 0:
            interval = INTERVAL_FIRST
        elif state.interval == INTERVAL_FIRST:
            interval = INTERVAL_SECOND
        else:
            interval = max(1, round(state.interval * ease))

    next_due = add_days_iso(interval)
    return SRSState(interval=interval, ease=ease, reps=reps), next_due
