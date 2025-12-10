"""
Tests for statistics API endpoints.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import SessionStatusEnum
from app.models import Exercise, ExerciseSession, User, Workout, WorkoutPlan, WorkoutSession


class TestStatsOverview:
    """Tests for GET /api/v1/stats/overview"""

    def test_stats_overview_success(self, client: TestClient, auth_headers: dict):
        """Test getting stats overview."""
        response = client.get("/api/v1/stats/overview", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_workouts" in data["data"]
        assert "total_duration_seconds" in data["data"]
        assert "total_volume_kg" in data["data"]
        assert "workouts_by_month" in data["data"]
        assert "most_trained_muscle_groups" in data["data"]
        assert "current_streak_days" in data["data"]
        assert "personal_records_count" in data["data"]

    def test_stats_overview_with_completed_sessions(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_workout_plan: WorkoutPlan,
        test_workout: Workout,
        test_exercise: Exercise,
    ):
        """Test stats overview with completed workout sessions."""
        # Create a completed session
        session = WorkoutSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            workout_plan_id=test_workout_plan.id,
            workout_id=test_workout.id,
            status=SessionStatusEnum.COMPLETED,
            created_at=datetime.utcnow() - timedelta(hours=1),
        )
        db.add(session)
        db.commit()

        # Add exercise session
        exercise_session = ExerciseSession(
            id=uuid.uuid4(),
            workout_session_id=session.id,
            exercise_id=test_exercise.id,
            weight=Decimal("50.0"),
            reps=10,
            set_number=1,
        )
        db.add(exercise_session)
        db.commit()

        response = client.get("/api/v1/stats/overview", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_workouts"] >= 1

        # Cleanup
        db.delete(exercise_session)
        db.delete(session)
        db.commit()

    def test_stats_overview_date_filter(self, client: TestClient, auth_headers: dict):
        """Test stats overview with date filters."""
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        end_date = datetime.utcnow().isoformat()

        response = client.get(
            f"/api/v1/stats/overview?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_stats_overview_empty(self, client: TestClient, auth_headers_user2: dict):
        """Test stats overview when user has no data."""
        response = client.get("/api/v1/stats/overview", headers=auth_headers_user2)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_workouts"] == 0
        assert data["data"]["total_duration_seconds"] == 0

    def test_stats_overview_unauthorized(self, client: TestClient):
        """Test stats overview without authentication."""
        response = client.get("/api/v1/stats/overview")

        assert response.status_code == 401


class TestExerciseHistory:
    """Tests for GET /api/v1/stats/exercise/{exercise_id}/history"""

    def test_exercise_history_success(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test getting exercise history."""
        response = client.get(
            f"/api/v1/stats/exercise/{test_exercise.id}/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "exercise" in data["data"]
        assert "sessions" in data["data"]
        assert data["data"]["exercise"]["id"] == str(test_exercise.id)

    def test_exercise_history_with_data(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_workout_plan: WorkoutPlan,
        test_workout: Workout,
        test_exercise: Exercise,
    ):
        """Test exercise history with workout data."""
        # Create a completed session
        session = WorkoutSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            workout_plan_id=test_workout_plan.id,
            workout_id=test_workout.id,
            status=SessionStatusEnum.COMPLETED,
            created_at=datetime.utcnow() - timedelta(hours=1),
        )
        db.add(session)
        db.commit()

        # Add exercise sessions (multiple sets)
        for i in range(3):
            exercise_session = ExerciseSession(
                id=uuid.uuid4(),
                workout_session_id=session.id,
                exercise_id=test_exercise.id,
                weight=Decimal("50.0"),
                reps=10,
                set_number=i + 1,
            )
            db.add(exercise_session)
        db.commit()

        response = client.get(
            f"/api/v1/stats/exercise/{test_exercise.id}/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["sessions"]) >= 1

        # Check session data
        history_session = data["data"]["sessions"][0]
        assert "date" in history_session
        assert "total_volume" in history_session
        assert "total_reps" in history_session
        assert "max_weight" in history_session
        assert "sets" in history_session

        # Cleanup
        db.query(ExerciseSession).filter(ExerciseSession.workout_session_id == session.id).delete()
        db.delete(session)
        db.commit()

    def test_exercise_history_date_filter(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test exercise history with date filters."""
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        end_date = datetime.utcnow().isoformat()

        response = client.get(
            f"/api/v1/stats/exercise/{test_exercise.id}/history?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_exercise_history_limit(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test exercise history respects limit."""
        response = client.get(
            f"/api/v1/stats/exercise/{test_exercise.id}/history?limit=5",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["sessions"]) <= 5

    def test_exercise_history_not_found(self, client: TestClient, auth_headers: dict):
        """Test exercise history for non-existent exercise."""
        fake_id = uuid.uuid4()
        response = client.get(
            f"/api/v1/stats/exercise/{fake_id}/history",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_exercise_history_unauthorized(self, client: TestClient, test_exercise: Exercise):
        """Test exercise history without authentication."""
        response = client.get(f"/api/v1/stats/exercise/{test_exercise.id}/history")

        assert response.status_code == 401
