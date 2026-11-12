"""Digital logic state representations and operations."""

from __future__ import annotations

from enum import Enum
from typing import Any

from manim.utils.color import RED, ManimColor

__all__ = [
    "LogicState",
    "logic_not",
    "logic_and",
    "logic_or",
    "logic_xor",
    "logic_nand",
    "logic_nor",
    "logic_xnor",
    "color_for_state",
]


class LogicState(Enum):
    """IEEE 1164 four-state logic values."""

    LOW = 0
    HIGH = 1
    HIGH_Z = 2
    UNDEFINED = 3

    def __str__(self) -> str:
        match self:
            case LogicState.LOW:
                return "0"
            case LogicState.HIGH:
                return "1"
            case LogicState.HIGH_Z:
                return "Z"
            case LogicState.UNDEFINED:
                return "X"

    def __repr__(self) -> str:
        return f"LogicState.{self.name}"

    def to_int(self) -> int | None:
        """Return integer 0 or 1, or None for non-binary states."""
        if self == LogicState.LOW:
            return 0
        if self == LogicState.HIGH:
            return 1
        return None

    def is_binary(self) -> bool:
        """Return True if this state is either LOW or HIGH."""
        return self in (LogicState.LOW, LogicState.HIGH)

    @classmethod
    def from_bool(cls, value: bool) -> LogicState:
        """Convert a boolean value to LogicState.HIGH or LogicState.LOW."""
        return cls.HIGH if value else cls.LOW

    @classmethod
    def parse(cls, value: Any) -> LogicState:
        """Convert a variety of types into a valid LogicState."""
        if isinstance(value, LogicState):
            return value
        if isinstance(value, bool):
            return cls.HIGH if value else cls.LOW
        if isinstance(value, (int, float)):
            if int(value) == 0:
                return cls.LOW
            if int(value) == 1:
                return cls.HIGH
            return cls.UNDEFINED
        if isinstance(value, str):
            clean = value.strip().upper()
            if clean in ("0", "LOW", "F", "FALSE", "L"):
                return cls.LOW
            if clean in ("1", "HIGH", "T", "TRUE", "H"):
                return cls.HIGH
            if clean in ("Z", "HIGH_Z", "HIGHZ", "FLOAT"):
                return cls.HIGH_Z
            if clean in ("X", "UNDEF", "UNDEFINED", "?"):
                return cls.UNDEFINED
        return cls.UNDEFINED


def logic_not(state: LogicState | Any) -> LogicState:
    """Evaluate logical NOT on a LogicState."""
    s = LogicState.parse(state)
    if s == LogicState.LOW:
        return LogicState.HIGH
    if s == LogicState.HIGH:
        return LogicState.LOW
    return s


def logic_and(*states: LogicState | Any) -> LogicState:
    """Evaluate logical AND across multiple LogicStates."""
    if not states:
        return LogicState.HIGH
    parsed = [LogicState.parse(s) for s in states]
    if any(s == LogicState.LOW for s in parsed):
        return LogicState.LOW
    if any(s in (LogicState.UNDEFINED, LogicState.HIGH_Z) for s in parsed):
        return LogicState.UNDEFINED
    return LogicState.HIGH


def logic_or(*states: LogicState | Any) -> LogicState:
    """Evaluate logical OR across multiple LogicStates."""
    if not states:
        return LogicState.LOW
    parsed = [LogicState.parse(s) for s in states]
    if any(s == LogicState.HIGH for s in parsed):
        return LogicState.HIGH
    if any(s in (LogicState.UNDEFINED, LogicState.HIGH_Z) for s in parsed):
        return LogicState.UNDEFINED
    return LogicState.LOW


def logic_xor(*states: LogicState | Any) -> LogicState:
    """Evaluate logical XOR (odd parity) across multiple LogicStates."""
    if not states:
        return LogicState.LOW
    parsed = [LogicState.parse(s) for s in states]
    if any(s in (LogicState.UNDEFINED, LogicState.HIGH_Z) for s in parsed):
        return LogicState.UNDEFINED
    ones = sum(1 for s in parsed if s == LogicState.HIGH)
    return LogicState.HIGH if (ones % 2 == 1) else LogicState.LOW


def logic_nand(*states: LogicState | Any) -> LogicState:
    """Evaluate logical NAND."""
    return logic_not(logic_and(*states))


def logic_nor(*states: LogicState | Any) -> LogicState:
    """Evaluate logical NOR."""
    return logic_not(logic_or(*states))


def logic_xnor(*states: LogicState | Any) -> LogicState:
    """Evaluate logical XNOR."""
    return logic_not(logic_xor(*states))


# Standard semantic color mapping for logic states in dark/light themes
STATE_COLORS: dict[LogicState, ManimColor] = {
    LogicState.HIGH: ManimColor("#2ECC71"),  # Vibrant Green
    LogicState.LOW: ManimColor("#4A4A4A"),  # Slate / Ground Gray
    LogicState.HIGH_Z: ManimColor("#3498DB"),  # Cyan / Floating Blue
    LogicState.UNDEFINED: ManimColor(RED),  # Red / Contention
}


def color_for_state(state: LogicState | Any) -> ManimColor:
    """Return the theme color corresponding to the given logic state."""
    parsed = LogicState.parse(state)
    return STATE_COLORS.get(parsed, ManimColor(RED))
