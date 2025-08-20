from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

@dataclass
class SRSState:
    interval: int = 0   # days
    ease: float = 2.5   # ease factor
    reps: int = 0       # successful reps

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def add_days_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).replace(microsecond=0).isoformat()

def review(state: SRSState | None, quality: int) -> tuple[SRSState, str]:
    """
    SM-2 inspired scheduler:
      - quality 0–2: lapse → interval=1, ease-=0.2 (min 1.3), reps=0
      - quality 3–5: success → ease += (0.1 - (5-q)*(0.08 + (5-q)*0.02))
                      interval progression: 1, 6, otherwise round(prev*ease)
    Returns: (new_state, next_due_iso)
    """
    if state is None:
        state = SRSState()

    ease = state.ease
    reps = state.reps

    if quality < 3:
        ease = max(1.3, ease - 0.2)
        interval = 1
        reps = 0
    else:
        delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        ease = max(1.3, ease + delta)
        reps += 1
        if state.interval == 0:
            interval = 1
        elif state.interval == 1:
            interval = 6
        else:
            interval = max(1, round(state.interval * ease))

    next_due = add_days_iso(interval)
    return SRSState(interval=interval, ease=ease, reps=reps), next_due
