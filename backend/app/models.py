import uuid
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import (
    ConfidenceLevelEnum,
    MuscleGroupEnum,
    RecordTypeEnum,
    SessionStatusEnum,
    UnitSystemEnum,
)


class User(Base):
    """User account information and preferences"""

    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    unit_system = Column(
        Enum(
            UnitSystemEnum,
            native_enum=True,
            create_constraint=True,
            values_callable=lambda e: [x.value for x in e],
        ),
        nullable=False,
        default=UnitSystemEnum.METRIC,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    workout_plans = relationship("WorkoutPlan", back_populates="user")
    workout_sessions = relationship("WorkoutSession", back_populates="user")
    personal_records = relationship("PersonalRecord", back_populates="user")
    workout_import_logs = relationship("WorkoutImportLog", back_populates="user")
    user_equipment = relationship("UserEquipment", back_populates="user")
    custom_exercises = relationship("Exercise", back_populates="user")

    __table_args__ = (Index("idx_user_email", "email"),)


class Equipment(Base):
    """Global reference table for all available equipment"""

    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    exercise_equipment = relationship("ExerciseEquipment", back_populates="equipment")
    user_equipment = relationship("UserEquipment", back_populates="equipment")

    __table_args__ = (Index("idx_equipment_name", "name"),)


class Exercise(Base):
    """Global exercise database with muscle groups and default parameters"""

    __tablename__ = "exercise"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    primary_muscle_groups = Column(
        ARRAY(
            Enum(
                MuscleGroupEnum,
                name="muscle_group_enum",
                native_enum=True,
                create_constraint=False,
                values_callable=lambda e: [x.value for x in e],
            )
        ),
        nullable=False,
    )
    secondary_muscle_groups = Column(
        ARRAY(
            Enum(
                MuscleGroupEnum,
                name="muscle_group_enum",
                native_enum=True,
                create_constraint=False,
                values_callable=lambda e: [x.value for x in e],
            )
        ),
        nullable=False,
        default=list,
    )
    default_weight = Column(Numeric(10, 2), nullable=True)
    default_reps = Column(Integer, nullable=True)
    default_rest_time_seconds = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    is_custom = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    exercise_equipment = relationship("ExerciseEquipment", back_populates="exercise")
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")
    exercise_sessions = relationship("ExerciseSession", back_populates="exercise")
    personal_records = relationship("PersonalRecord", back_populates="exercise")
    user = relationship("User", back_populates="custom_exercises")

    __table_args__ = (
        Index("idx_exercise_name", "name"),
        Index(
            "idx_exercise_primary_muscle_groups",
            "primary_muscle_groups",
            postgresql_using="gin",
        ),
        Index(
            "idx_exercise_secondary_muscle_groups",
            "secondary_muscle_groups",
            postgresql_using="gin",
        ),
        Index("idx_exercise_user_id", "user_id", postgresql_where="is_custom = true"),
        # Unique constraint: name must be unique for global exercises (user_id IS NULL)
        # and unique per user for custom exercises
        UniqueConstraint("name", "user_id", name="uq_exercise_name_user"),
    )


class ExerciseEquipment(Base):
    """Links exercises to required equipment (many-to-many)"""

    __tablename__ = "exercise_equipment"

    exercise_id = Column(
        UUID(as_uuid=True), ForeignKey("exercise.id"), primary_key=True, nullable=False
    )
    equipment_id = Column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), primary_key=True, nullable=False
    )

    # Relationships
    exercise = relationship("Exercise", back_populates="exercise_equipment")
    equipment = relationship("Equipment", back_populates="exercise_equipment")

    __table_args__ = (Index("idx_exercise_equipment_equipment_id", "equipment_id"),)


class UserEquipment(Base):
    """Links users to their available equipment (many-to-many, with soft delete)"""

    __tablename__ = "user_equipment"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, nullable=False)
    equipment_id = Column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), primary_key=True, nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_equipment")
    equipment = relationship("Equipment", back_populates="user_equipment")

    __table_args__ = (
        Index(
            "idx_user_equipment_user_id",
            "user_id",
            postgresql_where="deleted_at IS NULL",
        ),
        Index("idx_user_equipment_equipment_id", "equipment_id"),
    )


class WorkoutPlan(Base):
    """User-owned workout plan templates with soft delete support"""

    __tablename__ = "workout_plan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="workout_plans")
    workouts = relationship("Workout", back_populates="workout_plan", cascade="all, delete-orphan")
    workout_sessions = relationship("WorkoutSession", back_populates="workout_plan")
    workout_import_logs = relationship("WorkoutImportLog", back_populates="workout_plan")

    __table_args__ = (
        Index(
            "idx_workout_plan_user_id",
            "user_id",
            postgresql_where="deleted_at IS NULL",
        ),
        Index("idx_workout_plan_created_at", "user_id", "created_at"),
        Index(
            "idx_workout_plan_name",
            "user_id",
            "name",
            postgresql_where="deleted_at IS NULL",
        ),
    )


class Workout(Base):
    """Individual workout within a workout plan (e.g., "Day 1", "Push Day")"""

    __tablename__ = "workout"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_plan_id = Column(UUID(as_uuid=True), ForeignKey("workout_plan.id"), nullable=False)
    name = Column(String(255), nullable=False)
    day_number = Column(Integer, nullable=True)  # Optional day number
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    workout_plan = relationship("WorkoutPlan", back_populates="workouts")
    workout_exercises = relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    workout_sessions = relationship("WorkoutSession", back_populates="workout")

    __table_args__ = (
        Index("idx_workout_workout_plan_id", "workout_plan_id"),
        Index("idx_workout_order", "workout_plan_id", "order_index"),
    )


class WorkoutExercise(Base):
    """Exercises within a specific workout with workout-specific parameters"""

    __tablename__ = "workout_exercise"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workout.id"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercise.id"), nullable=False)
    sequence = Column(Integer, nullable=False)
    set_configurations = Column(JSONB, nullable=False)  # Array of {set_number, reps_min, reps_max}
    rest_time_seconds = Column(Integer, nullable=True)
    confidence_level = Column(
        Enum(
            ConfidenceLevelEnum,
            native_enum=True,
            create_constraint=True,
            values_callable=lambda e: [x.value for x in e],
        ),
        nullable=False,
        default=ConfidenceLevelEnum.MEDIUM,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    workout = relationship("Workout", back_populates="workout_exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")

    __table_args__ = (
        UniqueConstraint("workout_id", "sequence"),
        Index("idx_workout_exercise_workout_id", "workout_id"),
        Index("idx_workout_exercise_exercise_id", "exercise_id"),
        Index("idx_workout_exercise_sequence", "workout_id", "sequence"),
    )


class WorkoutSession(Base):
    """Individual workout execution records with status tracking"""

    __tablename__ = "workout_session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    workout_plan_id = Column(UUID(as_uuid=True), ForeignKey("workout_plan.id"), nullable=False)
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workout.id"), nullable=False)
    status = Column(
        Enum(
            SessionStatusEnum,
            native_enum=True,
            create_constraint=True,
            values_callable=lambda e: [x.value for x in e],
        ),
        nullable=False,
        default=SessionStatusEnum.IN_PROGRESS,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="workout_sessions")
    workout_plan = relationship("WorkoutPlan", back_populates="workout_sessions")
    workout = relationship("Workout", back_populates="workout_sessions")
    exercise_sessions = relationship("ExerciseSession", back_populates="workout_session")

    __table_args__ = (
        Index(
            "idx_workout_session_user_id",
            "user_id",
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "idx_workout_session_user_status_created",
            "user_id",
            "status",
            "created_at",
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "idx_workout_session_user_created",
            "user_id",
            "created_at",
            postgresql_where="deleted_at IS NULL",
        ),
        Index("idx_workout_session_workout_plan_id", "workout_plan_id"),
        Index("idx_workout_session_workout_id", "workout_id"),
    )


class ExerciseSession(Base):
    """Individual logged sets within a workout session (mutable records)"""

    __tablename__ = "exercise_session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_session_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_session.id"), nullable=False
    )
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercise.id"), nullable=False)
    weight = Column(Numeric(10, 2), nullable=False)
    reps = Column(Integer, nullable=False)
    rest_time_seconds = Column(Integer, nullable=True)
    set_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    workout_session = relationship("WorkoutSession", back_populates="exercise_sessions")
    exercise = relationship("Exercise", back_populates="exercise_sessions")
    personal_records = relationship("PersonalRecord", back_populates="exercise_session")

    __table_args__ = (
        Index("idx_exercise_session_workout_session_id", "workout_session_id"),
        Index("idx_exercise_session_exercise_id", "exercise_id"),
        Index("idx_exercise_session_user_exercise", "workout_session_id", "exercise_id"),
    )


class PersonalRecord(Base):
    """Denormalized personal record tracking for fast retrieval"""

    __tablename__ = "personal_record"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercise.id"), nullable=False)
    record_type = Column(
        Enum(
            RecordTypeEnum,
            native_enum=True,
            create_constraint=True,
            values_callable=lambda e: [x.value for x in e],
        ),
        nullable=False,
    )
    value = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(10), nullable=True)
    exercise_session_id = Column(
        UUID(as_uuid=True), ForeignKey("exercise_session.id"), nullable=True
    )
    achieved_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="personal_records")
    exercise = relationship("Exercise", back_populates="personal_records")
    exercise_session = relationship("ExerciseSession", back_populates="personal_records")

    __table_args__ = (
        UniqueConstraint("user_id", "exercise_id", "record_type"),
        Index("idx_personal_record_user_exercise", "user_id", "exercise_id"),
        Index("idx_personal_record_user_id", "user_id"),
        Index("idx_personal_record_achieved_at", "user_id", "achieved_at"),
    )


class WorkoutImportLog(Base):
    """Audit trail for AI parsing and import history"""

    __tablename__ = "workout_import_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    workout_plan_id = Column(UUID(as_uuid=True), ForeignKey("workout_plan.id"), nullable=True)
    raw_text = Column(Text, nullable=False)
    parsed_exercises = Column(JSONB, nullable=True)
    confidence_scores = Column(JSONB, nullable=True)
    status = Column(String(50), nullable=False, default='pending')  # pending, processing, completed, failed
    result = Column(JSONB, nullable=True)  # Full parse result when completed
    error = Column(Text, nullable=True)  # Error message if failed
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workout_import_logs")
    workout_plan = relationship("WorkoutPlan", back_populates="workout_import_logs")

    __table_args__ = (
        Index("idx_workout_import_log_user_id", "user_id"),
        Index("idx_workout_import_log_workout_plan_id", "workout_plan_id"),
        Index("idx_workout_import_log_created_at", "user_id", "created_at"),
    )
