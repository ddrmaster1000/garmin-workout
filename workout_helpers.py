"""Additional helper functions for distance-based workout steps.

These extend the garminconnect.workout module with distance-based helpers.

IMPORTANT: For swimming workouts, Garmin uses conditionTypeId 3 for distance,
not conditionTypeId 1 (which is for lap button). This is different from the
garminconnect library's ConditionType.DISTANCE constant.
"""

from typing import Any
from garminconnect.workout import ExecutableStep, StepType, TargetType


def create_warmup_step_distance(
    distance: float,
    step_order: int = 1,
    target_type: dict[str, Any] | None = None,
    description: str | None = None,
) -> ExecutableStep:
    """Create a warmup step with distance-based duration.
    
    Note: Uses conditionTypeId 3 for swimming distance (not 1).
    
    Args:
        distance: Distance in yards for swimming
        step_order: Step order number
        target_type: Optional target type configuration
        description: Optional step description/notes
    """
    return ExecutableStep(
        stepOrder=step_order,
        stepType={
            "stepTypeId": StepType.WARMUP,
            "stepTypeKey": "warmup",
            "displayOrder": 1,
        },
        endCondition={
            "conditionTypeId": 3,  # Swimming distance uses 3, not 1
            "conditionTypeKey": "distance",
            "displayOrder": 3,
            "displayable": True,
        },
        endConditionValue=distance,
        targetType=target_type
        or {
            "workoutTargetTypeId": TargetType.NO_TARGET,
            "workoutTargetTypeKey": "no.target",
            "displayOrder": 1,
        },
        description=description,
    )


def create_interval_step_distance(
    distance: float,
    step_order: int,
    target_type: dict[str, Any] | None = None,
    description: str | None = None,
) -> ExecutableStep:
    """Create an interval step with distance-based duration.
    
    Note: Uses conditionTypeId 3 for swimming distance (not 1).
    
    Args:
        distance: Distance in yards for swimming
        step_order: Step order number
        target_type: Optional target type configuration
        description: Optional step description/notes
    """
    return ExecutableStep(
        stepOrder=step_order,
        stepType={
            "stepTypeId": StepType.INTERVAL,
            "stepTypeKey": "interval",
            "displayOrder": 3,
        },
        endCondition={
            "conditionTypeId": 3,  # Swimming distance uses 3, not 1
            "conditionTypeKey": "distance",
            "displayOrder": 3,
            "displayable": True,
        },
        endConditionValue=distance,
        targetType=target_type
        or {
            "workoutTargetTypeId": TargetType.NO_TARGET,
            "workoutTargetTypeKey": "no.target",
            "displayOrder": 1,
        },
        description=description,
    )


def create_recovery_step_distance(
    distance: float,
    step_order: int,
    target_type: dict[str, Any] | None = None,
    description: str | None = None,
) -> ExecutableStep:
    """Create a recovery step with distance-based duration.
    
    Note: Uses conditionTypeId 3 for swimming distance (not 1).
    
    Args:
        distance: Distance in yards for swimming
        step_order: Step order number
        target_type: Optional target type configuration
        description: Optional step description/notes
    """
    return ExecutableStep(
        stepOrder=step_order,
        stepType={
            "stepTypeId": StepType.RECOVERY,
            "stepTypeKey": "recovery",
            "displayOrder": 4,
        },
        endCondition={
            "conditionTypeId": 3,  # Swimming distance uses 3, not 1
            "conditionTypeKey": "distance",
            "displayOrder": 3,
            "displayable": True,
        },
        endConditionValue=distance,
        targetType=target_type
        or {
            "workoutTargetTypeId": TargetType.NO_TARGET,
            "workoutTargetTypeKey": "no.target",
            "displayOrder": 1,
        },
        description=description,
    )


def create_cooldown_step_distance(
    distance: float,
    step_order: int,
    target_type: dict[str, Any] | None = None,
    description: str | None = None,
) -> ExecutableStep:
    """Create a cooldown step with distance-based duration.
    
    Note: Uses conditionTypeId 3 for swimming distance (not 1).
    
    Args:
        distance: Distance in yards for swimming
        step_order: Step order number
        target_type: Optional target type configuration
        description: Optional step description/notes
    """
    return ExecutableStep(
        stepOrder=step_order,
        stepType={
            "stepTypeId": StepType.COOLDOWN,
            "stepTypeKey": "cooldown",
            "displayOrder": 2,
        },
        endCondition={
            "conditionTypeId": 3,  # Swimming distance uses 3, not 1
            "conditionTypeKey": "distance",
            "displayOrder": 3,
            "displayable": True,
        },
        endConditionValue=distance,
        targetType=target_type
        or {
            "workoutTargetTypeId": TargetType.NO_TARGET,
            "workoutTargetTypeKey": "no.target",
            "displayOrder": 1,
        },
        description=description,
    )


# Effort-based target helpers for swimming workouts
def create_effort_target(effort_level: int) -> dict[str, Any]:
    """Create an effort-based target for swimming workouts.
    
    Args:
        effort_level: Effort level from 1-5 (1=easy, 5=max effort)
        
    Returns:
        Dictionary with target configuration including secondaryTargetType
    """
    return {
        "targetType": {
            "workoutTargetTypeId": TargetType.NO_TARGET,
            "workoutTargetTypeKey": "no.target",
            "displayOrder": 1,
        },
        "secondaryTargetType": {
            "workoutTargetTypeId": 18,
            "workoutTargetTypeKey": "swim.instruction",
            "displayOrder": 18,
        },
        "secondaryTargetValueOne": float(effort_level),
        "secondaryTargetValueTwo": 0.0,
    }


def create_warmup_step_distance_effort(
    distance: float,
    step_order: int,
    effort_level: int,
    description: str | None = None,
) -> ExecutableStep:
    """Create a warmup step with distance and effort-based target.
    
    Args:
        distance: Distance in yards for swimming
        step_order: Step order number
        effort_level: Effort level 1-5 (1=easy, 5=max)
        description: Optional step description/notes
    """
    effort_config = create_effort_target(effort_level)
    
    return ExecutableStep(
        stepOrder=step_order,
        stepType={
            "stepTypeId": StepType.WARMUP,
            "stepTypeKey": "warmup",
            "displayOrder": 1,
        },
        endCondition={
            "conditionTypeId": 3,
            "conditionTypeKey": "distance",
            "displayOrder": 3,
            "displayable": True,
        },
        endConditionValue=distance,
        description=description,
        **effort_config
    )


def create_interval_step_distance_effort(
    distance: float,
    step_order: int,
    effort_level: int,
    description: str | None = None,
) -> ExecutableStep:
    """Create an interval step with distance and effort-based target.
    
    Args:
        distance: Distance in yards for swimming
        step_order: Step order number
        effort_level: Effort level 1-5 (1=easy, 5=max)
        description: Optional step description/notes
    """
    effort_config = create_effort_target(effort_level)
    
    return ExecutableStep(
        stepOrder=step_order,
        stepType={
            "stepTypeId": StepType.INTERVAL,
            "stepTypeKey": "interval",
            "displayOrder": 3,
        },
        endCondition={
            "conditionTypeId": 3,
            "conditionTypeKey": "distance",
            "displayOrder": 3,
            "displayable": True,
        },
        endConditionValue=distance,
        description=description,
        **effort_config
    )


def create_recovery_step_distance_effort(
    distance: float,
    step_order: int,
    effort_level: int,
    description: str | None = None,
) -> ExecutableStep:
    """Create a recovery step with distance and effort-based target.
    
    Args:
        distance: Distance in yards for swimming
        step_order: Step order number
        effort_level: Effort level 1-5 (1=easy, 5=max)
        description: Optional step description/notes
    """
    effort_config = create_effort_target(effort_level)
    
    return ExecutableStep(
        stepOrder=step_order,
        stepType={
            "stepTypeId": StepType.RECOVERY,
            "stepTypeKey": "recovery",
            "displayOrder": 4,
        },
        endCondition={
            "conditionTypeId": 3,
            "conditionTypeKey": "distance",
            "displayOrder": 3,
            "displayable": True,
        },
        endConditionValue=distance,
        description=description,
        **effort_config
    )


def create_cooldown_step_distance_effort(
    distance: float,
    step_order: int,
    effort_level: int,
    description: str | None = None,
) -> ExecutableStep:
    """Create a cooldown step with distance and effort-based target.
    
    Args:
        distance: Distance in yards for swimming
        step_order: Step order number
        effort_level: Effort level 1-5 (1=easy, 5=max)
        description: Optional step description/notes
    """
    effort_config = create_effort_target(effort_level)
    
    return ExecutableStep(
        stepOrder=step_order,
        stepType={
            "stepTypeId": StepType.COOLDOWN,
            "stepTypeKey": "cooldown",
            "displayOrder": 2,
        },
        endCondition={
            "conditionTypeId": 3,
            "conditionTypeKey": "distance",
            "displayOrder": 3,
            "displayable": True,
        },
        endConditionValue=distance,
        description=description,
        **effort_config
    )
