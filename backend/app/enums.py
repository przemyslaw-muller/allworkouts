import enum


class MuscleGroupEnum(str, enum.Enum):
    '''Muscle group enumeration'''

    CHEST = 'chest'
    BACK = 'back'
    SHOULDERS = 'shoulders'
    BICEPS = 'biceps'
    TRICEPS = 'triceps'
    FOREARMS = 'forearms'
    LEGS = 'legs'
    GLUTES = 'glutes'
    CORE = 'core'
    TRAPS = 'traps'
    LATS = 'lats'


class UnitSystemEnum(str, enum.Enum):
    '''Unit system preference'''

    METRIC = 'metric'
    IMPERIAL = 'imperial'


class ConfidenceLevelEnum(str, enum.Enum):
    '''AI parsing confidence level'''

    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class SessionStatusEnum(str, enum.Enum):
    '''Workout session status'''

    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'


class RecordTypeEnum(str, enum.Enum):
    '''Personal record type'''

    ONE_RM = '1rm'
    SET_VOLUME = 'set_volume'
    TOTAL_VOLUME = 'total_volume'
