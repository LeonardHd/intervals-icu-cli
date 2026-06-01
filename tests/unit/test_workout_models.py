import textwrap

from intervals_icu_cli.workout_models import (
    Workout,
    WorkoutStep,
    WorkoutStepTargetPace,
    WorkoutStepTargetPaceRange,
)


def build_sample_workout() -> Workout:
    return Workout(
        steps=[
            WorkoutStep(
                duration=120, target=WorkoutStepTargetPace(value=320, units="secs")
            ),
            WorkoutStep(
                label="Active",
                reps=3,
                steps=[
                    WorkoutStep(
                        label="active",
                        distance=2000,
                        target=WorkoutStepTargetPaceRange(
                            start=310, end=330, units="secs"
                        ),
                    ),
                    WorkoutStep(
                        duration=120,
                        intensity="recovery",
                        target=WorkoutStepTargetPace(value=360, units="secs"),
                    ),
                ],
            ),
        ]
    )


def test_workout_document_payload_contains_text_block():
    workout = build_sample_workout()

    expected_text = textwrap.dedent(
        """
        - 2m 5:20 Pace

        Active 3x
          - active 2km 5:10-5:30 Pace
          - 2m 6:00 Pace intensity=recovery
        """
    ).strip()

    assert workout.to_text() == expected_text
