import textwrap
from datetime import datetime

from intervals_icu_cli.mapper import map_event_create_request_to_intervals_api
from intervals_icu_cli.models import (
    EventCategory,
    EventCreateRequest,
    WorkoutType,
)
from intervals_icu_cli.workout_models import (
    Workout,
    WorkoutStep,
    WorkoutStepTargetPaceRange,
)


class TestSingleStepWorkouts:
    """Tests for EventCreateRequest with a single step workout."""

    def test_single_step_with_pace_range_and_distance_km(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    distance=10000,
                    target=WorkoutStepTargetPaceRange(start=300, end=330, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Easy 10k Recovery Run",
            date=datetime(2025, 12, 10, 8, 0, 0),
            workout=workout,
            category=EventCategory.WORKOUT,
            type=WorkoutType.RUN,
            description="Easy recovery run",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        assert result.name == "Easy 10k Recovery Run"
        assert result.start_date_local == "2025-12-10T08:00:00"
        assert result.category == "WORKOUT"
        assert result.type == "Run"

        expected_description = textwrap.dedent(
            """
            Easy recovery run
            - 10km 5:00-5:30 Pace
            """
        ).strip()
        assert result.description == expected_description

    def test_single_step_with_pace_range_and_shorter_distance(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    distance=5000,
                    target=WorkoutStepTargetPaceRange(start=270, end=300, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Tempo 5k",
            date=datetime(2025, 12, 11, 7, 30, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="Tempo run",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        assert result.name == "Tempo 5k"
        assert result.start_date_local == "2025-12-11T07:30:00"

        expected_description = textwrap.dedent(
            """
            Tempo run
            - 5km 4:30-5:00 Pace
            """
        ).strip()
        assert result.description == expected_description

    def test_single_step_with_label_and_pace_range(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    label="Recovery Jog",
                    distance=3000,
                    target=WorkoutStepTargetPaceRange(start=360, end=390, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Easy Shake-out Run",
            date=datetime(2025, 12, 12, 18, 0, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="Pre-race shake-out",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        expected_description = textwrap.dedent(
            """
            Pre-race shake-out
            - Recovery Jog 3km 6:00-6:30 Pace
            """
        ).strip()
        assert result.description == expected_description

    def test_single_step_with_meters_distance(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    distance=1500,
                    target=WorkoutStepTargetPaceRange(start=240, end=270, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Track Workout",
            date=datetime(2025, 12, 13, 6, 0, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="Track session",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        expected_description = textwrap.dedent(
            """
            Track session
            - 1.5km 4:00-4:30 Pace
            """
        ).strip()
        assert result.description == expected_description


class TestThreeStepStructuredWorkouts:
    """Tests for workouts with warmup, intervals, and cooldown structure."""

    def test_warmup_intervals_cooldown_with_labeled_steps(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    label="Warmup",
                    distance=2000,
                    target=WorkoutStepTargetPaceRange(start=360, end=390, units="secs"),
                ),
                WorkoutStep(
                    label="Intervals",
                    reps=4,
                    steps=[
                        WorkoutStep(
                            label="Fast",
                            distance=400,
                            target=WorkoutStepTargetPaceRange(
                                start=210, end=240, units="secs"
                            ),
                        ),
                        WorkoutStep(
                            label="Recovery",
                            distance=200,
                            target=WorkoutStepTargetPaceRange(
                                start=390, end=420, units="secs"
                            ),
                        ),
                    ],
                ),
                WorkoutStep(
                    label="Cooldown",
                    distance=2000,
                    target=WorkoutStepTargetPaceRange(start=360, end=390, units="secs"),
                ),
            ]
        )

        event_request = EventCreateRequest(
            name="Track Tuesday - 4x400m",
            date=datetime(2025, 12, 9, 6, 0, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="Speed session at the track",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        assert result.name == "Track Tuesday - 4x400m"
        assert result.start_date_local == "2025-12-09T06:00:00"

        expected_description = textwrap.dedent(
            """
            Speed session at the track
            - Warmup 2km 6:00-6:30 Pace

            Intervals 4x
              - Fast 400m 3:30-4:00 Pace
              - Recovery 200m 6:30-7:00 Pace

            - Cooldown 2km 6:00-6:30 Pace
            """
        ).strip()
        assert result.description == expected_description

    def test_long_intervals_with_tempo_block(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    label="Easy Warmup",
                    distance=3000,
                    target=WorkoutStepTargetPaceRange(start=330, end=360, units="secs"),
                ),
                WorkoutStep(
                    label="Tempo Intervals",
                    reps=3,
                    steps=[
                        WorkoutStep(
                            label="Tempo",
                            distance=1000,
                            target=WorkoutStepTargetPaceRange(
                                start=270, end=285, units="secs"
                            ),
                        ),
                        WorkoutStep(
                            label="Float",
                            distance=500,
                            target=WorkoutStepTargetPaceRange(
                                start=330, end=360, units="secs"
                            ),
                        ),
                    ],
                ),
                WorkoutStep(
                    label="Easy Cooldown",
                    distance=2000,
                    target=WorkoutStepTargetPaceRange(start=360, end=390, units="secs"),
                ),
            ]
        )

        event_request = EventCreateRequest(
            name="Tempo Thursday",
            date=datetime(2025, 12, 11, 5, 30, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="Tempo workout with float recovery",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        expected_description = textwrap.dedent(
            """
            Tempo workout with float recovery
            - Easy Warmup 3km 5:30-6:00 Pace

            Tempo Intervals 3x
              - Tempo 1km 4:30-4:45 Pace
              - Float 500m 5:30-6:00 Pace

            - Easy Cooldown 2km 6:00-6:30 Pace
            """
        ).strip()
        assert result.description == expected_description

    def test_fartlek_style_workout(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    label="Warmup Jog",
                    distance=2000,
                    target=WorkoutStepTargetPaceRange(start=360, end=420, units="secs"),
                ),
                WorkoutStep(
                    label="Fartlek",
                    reps=6,
                    steps=[
                        WorkoutStep(
                            label="Hard",
                            duration=90,
                            target=WorkoutStepTargetPaceRange(
                                start=255, end=285, units="secs"
                            ),
                        ),
                        WorkoutStep(
                            label="Easy",
                            duration=90,
                            target=WorkoutStepTargetPaceRange(
                                start=360, end=420, units="secs"
                            ),
                        ),
                    ],
                ),
                WorkoutStep(
                    label="Cooldown",
                    distance=1500,
                    target=WorkoutStepTargetPaceRange(start=360, end=420, units="secs"),
                ),
            ]
        )

        event_request = EventCreateRequest(
            name="Fartlek Friday",
            date=datetime(2025, 12, 12, 6, 30, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="Fun fartlek session",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        expected_description = textwrap.dedent(
            """
            Fun fartlek session
            - Warmup Jog 2km 6:00-7:00 Pace

            Fartlek 6x
              - Hard 1m 30s 4:15-4:45 Pace
              - Easy 1m 30s 6:00-7:00 Pace

            - Cooldown 1.5km 6:00-7:00 Pace
            """
        ).strip()
        assert result.description == expected_description


class TestMultiStepWorkouts:
    """Tests for workouts with multiple nested step structures."""

    def test_pyramid_workout_with_nested_intervals(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    label="Warmup",
                    distance=2000,
                    target=WorkoutStepTargetPaceRange(start=360, end=390, units="secs"),
                ),
                WorkoutStep(
                    label="Short Intervals",
                    reps=4,
                    steps=[
                        WorkoutStep(
                            label="Sprint",
                            distance=200,
                            target=WorkoutStepTargetPaceRange(
                                start=195, end=225, units="secs"
                            ),
                        ),
                        WorkoutStep(
                            label="Jog",
                            distance=200,
                            target=WorkoutStepTargetPaceRange(
                                start=390, end=420, units="secs"
                            ),
                        ),
                    ],
                ),
                WorkoutStep(
                    label="Medium Intervals",
                    reps=3,
                    steps=[
                        WorkoutStep(
                            label="Fast",
                            distance=400,
                            target=WorkoutStepTargetPaceRange(
                                start=225, end=255, units="secs"
                            ),
                        ),
                        WorkoutStep(
                            label="Recovery",
                            distance=400,
                            target=WorkoutStepTargetPaceRange(
                                start=360, end=390, units="secs"
                            ),
                        ),
                    ],
                ),
                WorkoutStep(
                    label="Long Intervals",
                    reps=2,
                    steps=[
                        WorkoutStep(
                            label="Tempo",
                            distance=800,
                            target=WorkoutStepTargetPaceRange(
                                start=255, end=285, units="secs"
                            ),
                        ),
                        WorkoutStep(
                            label="Float",
                            distance=400,
                            target=WorkoutStepTargetPaceRange(
                                start=330, end=360, units="secs"
                            ),
                        ),
                    ],
                ),
                WorkoutStep(
                    label="Cooldown",
                    distance=1500,
                    target=WorkoutStepTargetPaceRange(start=390, end=420, units="secs"),
                ),
            ]
        )

        event_request = EventCreateRequest(
            name="Pyramid Speed Session",
            date=datetime(2025, 12, 14, 7, 0, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="Pyramid intervals: 200m -> 400m -> 800m",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        assert result.name == "Pyramid Speed Session"

        expected_description = textwrap.dedent(
            """
            Pyramid intervals: 200m -> 400m -> 800m
            - Warmup 2km 6:00-6:30 Pace

            Short Intervals 4x
              - Sprint 200m 3:15-3:45 Pace
              - Jog 200m 6:30-7:00 Pace

            Medium Intervals 3x
              - Fast 400m 3:45-4:15 Pace
              - Recovery 400m 6:00-6:30 Pace

            Long Intervals 2x
              - Tempo 800m 4:15-4:45 Pace
              - Float 400m 5:30-6:00 Pace

            - Cooldown 1.5km 6:30-7:00 Pace
            """
        ).strip()
        assert result.description == expected_description

    def test_mixed_workout_multiple_blocks_without_nesting(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    label="Easy Start",
                    distance=3000,
                    target=WorkoutStepTargetPaceRange(start=360, end=390, units="secs"),
                ),
                WorkoutStep(
                    label="Progression 1",
                    distance=2000,
                    target=WorkoutStepTargetPaceRange(start=330, end=345, units="secs"),
                ),
                WorkoutStep(
                    label="Progression 2",
                    distance=2000,
                    target=WorkoutStepTargetPaceRange(start=300, end=315, units="secs"),
                ),
                WorkoutStep(
                    label="Progression 3",
                    distance=2000,
                    target=WorkoutStepTargetPaceRange(start=270, end=285, units="secs"),
                ),
                WorkoutStep(
                    label="Easy Finish",
                    distance=1000,
                    target=WorkoutStepTargetPaceRange(start=390, end=420, units="secs"),
                ),
            ]
        )

        event_request = EventCreateRequest(
            name="Progression Long Run",
            date=datetime(2025, 12, 15, 6, 0, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="10k progression run",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        expected_description = textwrap.dedent(
            """
            10k progression run
            - Easy Start 3km 6:00-6:30 Pace

            - Progression 1 2km 5:30-5:45 Pace

            - Progression 2 2km 5:00-5:15 Pace

            - Progression 3 2km 4:30-4:45 Pace

            - Easy Finish 1km 6:30-7:00 Pace
            """
        ).strip()
        assert result.description == expected_description


class TestEventRequestFieldMapping:
    """Tests to verify all EventCreateRequest fields are properly mapped to EventEx."""

    def test_none_description_handled(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    distance=5000,
                    target=WorkoutStepTargetPaceRange(start=300, end=330, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Simple Run",
            date=datetime(2025, 12, 10, 8, 0, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description=None,
        )

        result = map_event_create_request_to_intervals_api(event_request)

        assert result.name == "Simple Run"
        expected_description = "\n- 5km 5:00-5:30 Pace"
        assert result.description == expected_description

    def test_empty_description(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    distance=8000,
                    target=WorkoutStepTargetPaceRange(start=330, end=360, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Quick Run",
            date=datetime(2025, 12, 10, 12, 0, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        expected_description = "\n- 8km 5:30-6:00 Pace"
        assert result.description == expected_description

    def test_category_defaults_to_workout(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    distance=5000,
                    target=WorkoutStepTargetPaceRange(start=300, end=330, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Default Category Run",
            date=datetime(2025, 12, 10, 8, 0, 0),
            workout=workout,
            type=WorkoutType.RUN,
            description="Test run",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        assert result.category == "WORKOUT"

        expected_description = textwrap.dedent(
            """
            Test run
            - 5km 5:00-5:30 Pace
            """
        ).strip()
        assert result.description == expected_description

    def test_weight_training_type_passed_through(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    distance=5000,
                    target=WorkoutStepTargetPaceRange(start=300, end=330, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Strength Session",
            date=datetime(2025, 12, 10, 8, 0, 0),
            workout=workout,
            type=WorkoutType.WEIGHT_TRAINING,
            description="Strength",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        assert result.type == "WeightTraining"

    def test_microseconds_stripped_from_date(self):
        workout = Workout(
            steps=[
                WorkoutStep(
                    distance=5000,
                    target=WorkoutStepTargetPaceRange(start=300, end=330, units="secs"),
                )
            ]
        )

        event_request = EventCreateRequest(
            name="Precise Time Run",
            date=datetime(2025, 12, 10, 8, 30, 45, 123456),
            workout=workout,
            type=WorkoutType.RUN,
            description="Test",
        )

        result = map_event_create_request_to_intervals_api(event_request)

        assert result.start_date_local == "2025-12-10T08:30:45"
        assert "123456" not in result.start_date_local

        expected_description = textwrap.dedent(
            """
            Test
            - 5km 5:00-5:30 Pace
            """
        ).strip()
        assert result.description == expected_description
