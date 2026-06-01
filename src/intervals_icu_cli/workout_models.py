from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


def _format_duration(seconds: int) -> str:
    minutes, rem = divmod(seconds, 60)
    parts: list[str] = []
    if minutes:
        parts.append(f"{minutes}m")
    if rem:
        parts.append(f"{rem}s")
    if not parts:
        parts.append("0s")
    return " ".join(parts)


def _format_distance(meters: int) -> str:
    if meters % 1000 == 0:
        return f"{meters // 1000}km"
    if meters >= 1000:
        km = meters / 1000
        return f"{km:g}km"
    return f"{meters}m"


def _format_pace_value(value: int, units: str) -> str:
    if units == "secs":
        minutes, rem = divmod(value, 60)
        return f"{minutes}:{rem:02d}"
    return f"{value}{units}"


class WorkoutStepTarget(BaseModel):
    """Base class for structured workout targets (pace, power, etc.)."""

    pass


class WorkoutStepTargetPace(WorkoutStepTarget):
    value: int
    units: str


class WorkoutStepTargetPaceRange(WorkoutStepTarget):
    start: int
    end: int
    units: str


class WorkoutStep(BaseModel):
    label: Optional[str] = Field(default=None)
    duration: Optional[int] = None
    distance: Optional[int] = None
    reps: Optional[int] = None
    intensity: Optional[str] = None
    target: Optional[WorkoutStepTargetPace | WorkoutStepTargetPaceRange] = Field(
        default=None
    )
    steps: Optional[list["WorkoutStep"]] = Field(default_factory=list)

    def to_text_block(self, depth: int = 0) -> str:
        indent = "  " * depth
        if self.steps:
            header = f"{indent}{self._format_header()}"
            child_lines: list[str] = []
            for child in self.steps:
                child_lines.extend(child._collect_text_lines(depth + 1))
            block = "\n".join(line for line in [header, *child_lines] if line)
            return block
        return self._format_leaf_line(depth)

    def _collect_text_lines(self, depth: int) -> list[str]:
        block = self.to_text_block(depth)
        return block.split("\n") if block else []

    def _format_leaf_line(self, depth: int) -> str:
        content = self._format_leaf_content()
        prefix = f"{'  ' * depth}- "
        return f"{prefix}{content}" if content else "-"

    def _format_leaf_content(self) -> str:
        parts: list[str] = []
        if self.label:
            parts.append(self.label)
        if self.duration is not None:
            parts.append(_format_duration(self.duration))
        if self.distance is not None:
            parts.append(_format_distance(self.distance))

        target_text = self._format_target_text()
        if target_text:
            parts.append(target_text)

        if self.reps and not self.steps:
            parts.append(f"{self.reps}x")

        if self.intensity:
            parts.append(f"intensity={self.intensity}")

        return " ".join(parts).strip()

    def _format_header(self) -> str:
        pieces: list[str] = []
        if self.label:
            pieces.append(self.label)
        if self.duration is not None:
            pieces.append(_format_duration(self.duration))
        if self.distance is not None:
            pieces.append(_format_distance(self.distance))
        if self.reps:
            pieces.append(f"{self.reps}x")

        header = " ".join(pieces).strip()
        return header or "Workout"

    def _format_target_text(self) -> Optional[str]:
        target = self.target
        if target is None:
            return None
        if isinstance(target, WorkoutStepTargetPace):
            return f"{_format_pace_value(target.value, target.units)} Pace"
        if isinstance(target, WorkoutStepTargetPaceRange):
            first = _format_pace_value(target.start, target.units)
            second = _format_pace_value(target.end, target.units)
            return f"{first}-{second} Pace"
        return None


class Workout(BaseModel):
    steps: list[WorkoutStep] = Field(default_factory=list)

    def to_text(self) -> str:
        blocks: list[str] = []
        for step in self.steps:
            block = step.to_text_block()
            if block.strip():
                blocks.append(block)
        return "\n\n".join(blocks).strip()
