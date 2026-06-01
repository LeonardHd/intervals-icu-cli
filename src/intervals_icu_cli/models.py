from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel

from intervals_icu_cli.workout_models import Workout


class WorkoutType(StrEnum):
    # Cycling
    RIDE = "Ride"
    MTB = "MTB"
    GRAVEL_RIDE = "Gravel Ride"
    TRACK_CYCLING = "Track Cycling"
    VIRTUAL_RIDE = "Virtual Ride"
    E_BIKE_RIDE = "E-Bike Ride"
    E_MTB_RIDE = "E-MTB Ride"
    HANDCYCLE = "Handcycle"
    VELOMOBILE = "Velomobile"

    # Running
    RUN = "Run"
    TRAIL_RUN = "Trail Run"
    VIRTUAL_RUN = "Virtual Run"

    # Swimming
    SWIM = "Swim"
    OPEN_WATER_SWIM = "Open Water Swim"

    # Winter Sports
    ALPINE_SKI = "Alpine Ski"
    BACKCOUNTRY_SKI = "Backcountry Ski"
    NORDIC_SKI = "Nordic Ski"
    VIRTUAL_SKI = "Virtual Ski"
    SNOWBOARD = "Snowboard"
    SNOWSHOE = "Snowshoe"
    ICE_SKATE = "Ice Skate"
    ROLLER_SKI = "Roller Ski"

    # Water Sports
    CANOEING = "Canoeing"
    KAYAKING = "Kayaking"
    KITESURF = "Kitesurf"
    ROWING = "Rowing"
    VIRTUAL_ROWING = "Virtual Rowing"
    SAIL = "Sail"
    STAND_UP_PADDLING = "Stand Up Paddling"
    SURFING = "Surfing"
    WINDSURF = "Windsurf"
    WATER_SPORT = "Water Sport"

    # Gym/Fitness
    WEIGHT_TRAINING = "WeightTraining"
    CROSSFIT = "Crossfit"
    ELLIPTICAL = "Elliptical"
    HIIT = "HIIT"
    PILATES = "Pilates"
    STAIR_STEPPER = "Stair-Stepper"
    WORKOUT = "Workout"
    YOGA = "Yoga"

    # Racket Sports
    BADMINTON = "Badminton"
    PADEL = "Padel"
    PICKLEBALL = "Pickleball"
    RACQUETBALL = "Racquetball"
    SQUASH = "Squash"
    TABLE_TENNIS = "Table Tennis"
    TENNIS = "Tennis"

    # Team Sports
    HOCKEY = "Hockey"
    RUGBY = "Rugby"
    SOCCER = "Soccer"

    # Other
    HIKE = "Hike"
    WALK = "Walk"
    GOLF = "Golf"
    INLINE_SKATE = "Inline Skate"
    ROCK_CLIMBING = "Rock Climbing"
    SKATEBOARD = "Skateboard"
    WHEELCHAIR = "Wheelchair"
    TRANSITION = "Transition"
    OTHER = "Other"


class EventCategory(StrEnum):
    WORKOUT = "WORKOUT"


class EventCreateRequest(BaseModel):
    name: str
    date: datetime
    workout: Workout
    category: EventCategory = EventCategory.WORKOUT
    type: Optional[WorkoutType] = None
    description: Optional[str] = None


class EventCreateResponse(BaseModel):
    id: int
    name: str
    date: str
    description: str
