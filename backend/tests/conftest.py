"""
Pytest fixtures for API tests.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import create_access_token, hash_password
from app.config import settings
from app.database import get_db
from app.enums import ConfidenceLevelEnum, MuscleGroupEnum, RecordTypeEnum, SessionStatusEnum
from app.main import app
from app.models import (
    Equipment,
    Exercise,
    ExerciseEquipment,
    ExerciseSession,
    PersonalRecord,
    User,
    UserEquipment,
    WorkoutExercise,
    WorkoutPlan,
    WorkoutSession,
)

# Test database engine - uses the same database as the app (Docker PostgreSQL)
engine = create_engine(settings.database_url, pool_pre_ping=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database session for testing."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Provide a clean database session for each test."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Provide a test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_2(db: Session) -> User:
    """Create a second test user for isolation tests."""
    user = User(
        id=uuid.uuid4(),
        email=f"test2_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword456"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for the test user."""
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2(test_user_2: User) -> dict:
    """Create authorization headers for the second test user."""
    token = create_access_token(str(test_user_2.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_equipment(db: Session) -> Generator[Equipment, None, None]:
    """Create test equipment."""
    equipment = Equipment(
        id=uuid.uuid4(),
        name=f"Test Equipment {uuid.uuid4().hex[:8]}",
        description="Test equipment description",
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    yield equipment
    # Cleanup
    db.query(ExerciseEquipment).filter(ExerciseEquipment.equipment_id == equipment.id).delete()
    db.query(UserEquipment).filter(UserEquipment.equipment_id == equipment.id).delete()
    db.query(Equipment).filter(Equipment.id == equipment.id).delete()
    db.commit()


@pytest.fixture
def test_equipment_2(db: Session) -> Generator[Equipment, None, None]:
    """Create additional test equipment."""
    equipment = Equipment(
        id=uuid.uuid4(),
        name=f"Test Equipment 2 {uuid.uuid4().hex[:8]}",
        description="Second test equipment description",
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    yield equipment
    # Cleanup
    db.query(ExerciseEquipment).filter(ExerciseEquipment.equipment_id == equipment.id).delete()
    db.query(UserEquipment).filter(UserEquipment.equipment_id == equipment.id).delete()
    db.query(Equipment).filter(Equipment.id == equipment.id).delete()
    db.commit()


@pytest.fixture
def test_exercise(db: Session) -> Generator[Exercise, None, None]:
    """Create a test exercise."""
    exercise = Exercise(
        id=uuid.uuid4(),
        name=f"Test Exercise {uuid.uuid4().hex[:8]}",
        primary_muscle_groups=[MuscleGroupEnum.CHEST],
        secondary_muscle_groups=[MuscleGroupEnum.TRICEPS],
        default_weight=Decimal("20.0"),
        default_reps=10,
        default_rest_time_seconds=90,
        description="Test exercise description",
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    yield exercise
    # Cleanup - order matters due to foreign key constraints
    # First delete personal records that reference exercise sessions for this exercise
    exercise_session_ids = [
        es.id
        for es in db.query(ExerciseSession).filter(ExerciseSession.exercise_id == exercise.id).all()
    ]
    if exercise_session_ids:
        db.query(PersonalRecord).filter(
            PersonalRecord.exercise_session_id.in_(exercise_session_ids)
        ).delete(synchronize_session=False)
    db.query(PersonalRecord).filter(PersonalRecord.exercise_id == exercise.id).delete()
    db.query(ExerciseSession).filter(ExerciseSession.exercise_id == exercise.id).delete()
    db.query(WorkoutExercise).filter(WorkoutExercise.exercise_id == exercise.id).delete()
    db.query(ExerciseEquipment).filter(ExerciseEquipment.exercise_id == exercise.id).delete()
    db.query(Exercise).filter(Exercise.id == exercise.id).delete()
    db.commit()


@pytest.fixture
def test_exercise_2(db: Session) -> Generator[Exercise, None, None]:
    """Create a second test exercise."""
    exercise = Exercise(
        id=uuid.uuid4(),
        name=f"Test Exercise 2 {uuid.uuid4().hex[:8]}",
        primary_muscle_groups=[MuscleGroupEnum.BACK],
        secondary_muscle_groups=[MuscleGroupEnum.BICEPS],
        default_weight=Decimal("30.0"),
        default_reps=8,
        default_rest_time_seconds=120,
        description="Second test exercise description",
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    yield exercise
    # Cleanup - order matters due to foreign key constraints
    # First delete personal records that reference exercise sessions for this exercise
    exercise_session_ids = [
        es.id
        for es in db.query(ExerciseSession).filter(ExerciseSession.exercise_id == exercise.id).all()
    ]
    if exercise_session_ids:
        db.query(PersonalRecord).filter(
            PersonalRecord.exercise_session_id.in_(exercise_session_ids)
        ).delete(synchronize_session=False)
    db.query(PersonalRecord).filter(PersonalRecord.exercise_id == exercise.id).delete()
    db.query(ExerciseSession).filter(ExerciseSession.exercise_id == exercise.id).delete()
    db.query(WorkoutExercise).filter(WorkoutExercise.exercise_id == exercise.id).delete()
    db.query(ExerciseEquipment).filter(ExerciseEquipment.exercise_id == exercise.id).delete()
    db.query(Exercise).filter(Exercise.id == exercise.id).delete()
    db.commit()


@pytest.fixture
def test_exercise_with_equipment(
    db: Session, test_exercise: Exercise, test_equipment: Equipment
) -> Exercise:
    """Link equipment to the test exercise."""
    exercise_equipment = ExerciseEquipment(
        exercise_id=test_exercise.id,
        equipment_id=test_equipment.id,
    )
    db.add(exercise_equipment)
    db.commit()
    return test_exercise


@pytest.fixture
def test_user_equipment(db: Session, test_user: User, test_equipment: Equipment) -> UserEquipment:
    """Create user equipment ownership."""
    user_equipment = UserEquipment(
        user_id=test_user.id,
        equipment_id=test_equipment.id,
    )
    db.add(user_equipment)
    db.commit()
    db.refresh(user_equipment)
    return user_equipment


@pytest.fixture
def test_workout_plan(db: Session, test_user: User) -> WorkoutPlan:
    """Create a test workout plan."""
    plan = WorkoutPlan(
        id=uuid.uuid4(),
        user_id=test_user.id,
        name=f"Test Workout Plan {uuid.uuid4().hex[:8]}",
        description="Test workout plan description",
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@pytest.fixture
def test_workout_plan_with_exercises(
    db: Session, test_workout_plan: WorkoutPlan, test_exercise: Exercise, test_exercise_2: Exercise
) -> WorkoutPlan:
    """Create a workout plan with exercises."""
    we1 = WorkoutExercise(
        id=uuid.uuid4(),
        workout_plan_id=test_workout_plan.id,
        exercise_id=test_exercise.id,
        sequence=1,
        sets=3,
        reps_min=8,
        reps_max=12,
        rest_time_seconds=90,
        confidence_level=ConfidenceLevelEnum.MEDIUM,
    )
    we2 = WorkoutExercise(
        id=uuid.uuid4(),
        workout_plan_id=test_workout_plan.id,
        exercise_id=test_exercise_2.id,
        sequence=2,
        sets=4,
        reps_min=6,
        reps_max=10,
        rest_time_seconds=120,
        confidence_level=ConfidenceLevelEnum.HIGH,
    )
    db.add(we1)
    db.add(we2)
    db.commit()
    db.refresh(test_workout_plan)
    return test_workout_plan


@pytest.fixture
def test_workout_session(
    db: Session, test_user: User, test_workout_plan: WorkoutPlan
) -> WorkoutSession:
    """Create a test workout session."""
    session = WorkoutSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        workout_plan_id=test_workout_plan.id,
        status=SessionStatusEnum.IN_PROGRESS,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@pytest.fixture
def test_completed_workout_session(
    db: Session, test_user: User, test_workout_plan: WorkoutPlan
) -> WorkoutSession:
    """Create a completed workout session."""
    session = WorkoutSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        workout_plan_id=test_workout_plan.id,
        status=SessionStatusEnum.COMPLETED,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@pytest.fixture
def test_exercise_session(
    db: Session, test_workout_session: WorkoutSession, test_exercise: Exercise
) -> ExerciseSession:
    """Create a test exercise session."""
    exercise_session = ExerciseSession(
        id=uuid.uuid4(),
        workout_session_id=test_workout_session.id,
        exercise_id=test_exercise.id,
        weight=Decimal("50.0"),
        reps=10,
        set_number=1,
        rest_time_seconds=90,
    )
    db.add(exercise_session)
    db.commit()
    db.refresh(exercise_session)
    return exercise_session


@pytest.fixture
def test_personal_record(
    db: Session, test_user: User, test_exercise: Exercise, test_exercise_session: ExerciseSession
) -> PersonalRecord:
    """Create a test personal record."""
    pr = PersonalRecord(
        id=uuid.uuid4(),
        user_id=test_user.id,
        exercise_id=test_exercise.id,
        record_type=RecordTypeEnum.ONE_RM,
        value=Decimal("100.0"),
        unit="kg",
        exercise_session_id=test_exercise_session.id,
        achieved_at=datetime.utcnow(),
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr
