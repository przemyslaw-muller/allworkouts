"""
Tests for workout sessions API endpoints.
"""

import uuid
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import SessionStatusEnum
from app.models import (
    Exercise,
    ExerciseSession,
    User,
    Workout,
    WorkoutPlan,
    WorkoutSession,
)


class TestListWorkoutSessions:
    """Tests for GET /api/v1/workout-sessions"""

    def test_list_workout_sessions_success(
        self, client: TestClient, auth_headers: dict, test_workout_session: WorkoutSession
    ):
        """Test listing workout sessions."""
        response = client.get("/api/v1/workout-sessions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sessions" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["sessions"]) >= 1

    def test_list_workout_sessions_filter_by_plan(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_session: WorkoutSession,
        test_workout_plan: WorkoutPlan,
    ):
        """Test filtering sessions by workout plan."""
        response = client.get(
            f"/api/v1/workout-sessions?workout_plan_id={test_workout_plan.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        for session in data["data"]["sessions"]:
            assert session["workout_plan"]["id"] == str(test_workout_plan.id)

    def test_list_workout_sessions_filter_by_status(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_session: WorkoutSession,
    ):
        """Test filtering sessions by status."""
        response = client.get(
            f"/api/v1/workout-sessions?status_filter={SessionStatusEnum.IN_PROGRESS.value}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        for session in data["data"]["sessions"]:
            assert session["status"] == SessionStatusEnum.IN_PROGRESS.value

    def test_list_workout_sessions_date_filter(
        self, client: TestClient, auth_headers: dict, test_workout_session: WorkoutSession
    ):
        """Test filtering sessions by date range."""
        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        end_date = datetime.utcnow().isoformat()

        response = client.get(
            f"/api/v1/workout-sessions?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_workout_sessions_pagination(
        self, client: TestClient, auth_headers: dict, test_workout_session: WorkoutSession
    ):
        """Test session list pagination."""
        response = client.get("/api/v1/workout-sessions?page=1&limit=5", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 5

    def test_list_workout_sessions_unauthorized(self, client: TestClient):
        """Test listing sessions without authentication."""
        response = client.get("/api/v1/workout-sessions")

        assert response.status_code == 401


class TestGetCurrentWorkoutSession:
    """Tests for GET /api/v1/workout-sessions/current"""

    def test_get_current_session_success(
        self, client: TestClient, auth_headers: dict, test_workout_session: WorkoutSession
    ):
        """Test getting current in-progress session."""
        response = client.get("/api/v1/workout-sessions/current", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data["data"]
        assert "workout_plan" in data["data"]
        assert "started_at" in data["data"]
        assert "exercises" in data["data"]

    def test_get_current_session_with_exercises(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_workout_plan_with_exercises: WorkoutPlan,
    ):
        """Test getting current session includes exercise context."""
        # Get the workout from the plan
        workout = (
            db.query(Workout)
            .filter(Workout.workout_plan_id == test_workout_plan_with_exercises.id)
            .first()
        )

        # Create an in-progress session for the test
        session = WorkoutSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            workout_plan_id=test_workout_plan_with_exercises.id,
            workout_id=workout.id,
            status=SessionStatusEnum.IN_PROGRESS,
        )
        db.add(session)
        db.commit()

        response = client.get("/api/v1/workout-sessions/current", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session_id"] == str(session.id)
        assert len(data["data"]["exercises"]) >= 1

        # Check exercise context
        for exercise in data["data"]["exercises"]:
            assert "planned_exercise_id" in exercise
            assert "exercise" in exercise
            assert "planned_sets" in exercise
            assert "context" in exercise

        # Cleanup
        db.delete(session)
        db.commit()

    def test_get_current_session_not_found(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_completed_workout_session: WorkoutSession,
    ):
        """Test 404 when no in-progress session exists."""
        response = client.get("/api/v1/workout-sessions/current", headers=auth_headers)

        assert response.status_code == 404

    def test_get_current_session_unauthorized(self, client: TestClient):
        """Test getting current session without authentication."""
        response = client.get("/api/v1/workout-sessions/current")

        assert response.status_code == 401


class TestGetWorkoutSession:
    """Tests for GET /api/v1/workout-sessions/{session_id}"""

    def test_get_workout_session_success(
        self, client: TestClient, auth_headers: dict, test_workout_session: WorkoutSession
    ):
        """Test getting workout session details."""
        response = client.get(
            f"/api/v1/workout-sessions/{test_workout_session.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(test_workout_session.id)
        assert "workout_plan" in data["data"]
        assert "status" in data["data"]
        assert "exercise_sessions" in data["data"]

    def test_get_workout_session_with_exercises(
        self,
        client: TestClient,
        auth_headers: dict,
        test_exercise_session: ExerciseSession,
        test_workout_session: WorkoutSession,
    ):
        """Test getting session includes exercise sessions."""
        response = client.get(
            f"/api/v1/workout-sessions/{test_workout_session.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["exercise_sessions"]) >= 1

        # Check exercise session details
        es = data["data"]["exercise_sessions"][0]
        assert "id" in es
        assert "exercise" in es
        assert "set_number" in es
        assert "weight" in es
        assert "reps" in es

    def test_get_workout_session_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent workout session."""
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/workout-sessions/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_get_workout_session_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout_session: WorkoutSession,
    ):
        """Test that user cannot access another user's workout session."""
        response = client.get(
            f"/api/v1/workout-sessions/{test_workout_session.id}",
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_get_workout_session_unauthorized(
        self, client: TestClient, test_workout_session: WorkoutSession
    ):
        """Test getting session without authentication."""
        response = client.get(f"/api/v1/workout-sessions/{test_workout_session.id}")

        assert response.status_code == 401


class TestStartWorkoutSession:
    """Tests for POST /api/v1/workout-sessions/start"""

    def test_start_workout_session_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_workout_plan_with_exercises: WorkoutPlan,
    ):
        """Test starting a new workout session."""
        # Get the workout from the plan
        workout = (
            db.query(Workout)
            .filter(Workout.workout_plan_id == test_workout_plan_with_exercises.id)
            .first()
        )
        assert workout is not None

        response = client.post(
            "/api/v1/workout-sessions/start",
            json={"workout_id": str(workout.id)},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data["data"]
        assert "workout_plan" in data["data"]
        assert "workout" in data["data"]
        assert "started_at" in data["data"]
        assert "exercises" in data["data"]

        # Check exercise context
        assert len(data["data"]["exercises"]) >= 1
        for exercise in data["data"]["exercises"]:
            assert "planned_exercise_id" in exercise
            assert "exercise" in exercise
            assert "planned_sets" in exercise
            assert "context" in exercise

        # Cleanup
        session_id = data["data"]["session_id"]
        db.query(WorkoutSession).filter(WorkoutSession.id == session_id).delete()
        db.commit()

    def test_start_workout_session_nonexistent_plan(self, client: TestClient, auth_headers: dict):
        """Test starting session with non-existent workout."""
        fake_id = uuid.uuid4()
        response = client.post(
            "/api/v1/workout-sessions/start",
            json={"workout_id": str(fake_id)},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_start_workout_session_other_user_plan(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout: Workout,
    ):
        """Test starting session with another user's workout."""
        response = client.post(
            "/api/v1/workout-sessions/start",
            json={"workout_id": str(test_workout.id)},
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_start_workout_session_unauthorized(self, client: TestClient, test_workout: Workout):
        """Test starting session without authentication."""
        response = client.post(
            "/api/v1/workout-sessions/start",
            json={"workout_id": str(test_workout.id)},
        )

        assert response.status_code == 401


class TestLogExercise:
    """Tests for POST /api/v1/workout-sessions/{session_id}/exercises"""

    def test_log_exercise_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_workout_session: WorkoutSession,
        test_exercise: Exercise,
    ):
        """Test logging exercise sets."""
        response = client.post(
            f"/api/v1/workout-sessions/{test_workout_session.id}/exercises",
            json={
                "exercise_id": str(test_exercise.id),
                "sets": [
                    {"set_number": 1, "weight": 50.0, "reps": 10, "rest_time_seconds": 90},
                    {"set_number": 2, "weight": 50.0, "reps": 9, "rest_time_seconds": 90},
                    {"set_number": 3, "weight": 50.0, "reps": 8, "rest_time_seconds": 90},
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "exercise_session_ids" in data["data"]
        assert len(data["data"]["exercise_session_ids"]) == 3

        # Cleanup
        for es_id in data["data"]["exercise_session_ids"]:
            db.query(ExerciseSession).filter(ExerciseSession.id == es_id).delete()
        db.commit()

    def test_log_exercise_session_not_found(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test logging to non-existent session."""
        fake_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/workout-sessions/{fake_id}/exercises",
            json={
                "exercise_id": str(test_exercise.id),
                "sets": [{"set_number": 1, "weight": 50.0, "reps": 10}],
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_log_exercise_session_not_in_progress(
        self,
        client: TestClient,
        auth_headers: dict,
        test_completed_workout_session: WorkoutSession,
        test_exercise: Exercise,
    ):
        """Test logging to a completed session."""
        response = client.post(
            f"/api/v1/workout-sessions/{test_completed_workout_session.id}/exercises",
            json={
                "exercise_id": str(test_exercise.id),
                "sets": [{"set_number": 1, "weight": 50.0, "reps": 10}],
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_log_exercise_invalid_exercise(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_session: WorkoutSession,
    ):
        """Test logging with non-existent exercise."""
        fake_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/workout-sessions/{test_workout_session.id}/exercises",
            json={
                "exercise_id": str(fake_id),
                "sets": [{"set_number": 1, "weight": 50.0, "reps": 10}],
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_log_exercise_unauthorized(
        self, client: TestClient, test_workout_session: WorkoutSession, test_exercise: Exercise
    ):
        """Test logging without authentication."""
        response = client.post(
            f"/api/v1/workout-sessions/{test_workout_session.id}/exercises",
            json={
                "exercise_id": str(test_exercise.id),
                "sets": [{"set_number": 1, "weight": 50.0, "reps": 10}],
            },
        )

        assert response.status_code == 401


class TestCompleteWorkoutSession:
    """Tests for POST /api/v1/workout-sessions/{session_id}/complete"""

    def test_complete_workout_session_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_workout_plan: WorkoutPlan,
        test_workout: Workout,
    ):
        """Test completing a workout session."""
        # Create a new session to complete
        session = WorkoutSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            workout_plan_id=test_workout_plan.id,
            workout_id=test_workout.id,
            status=SessionStatusEnum.IN_PROGRESS,
        )
        db.add(session)
        db.commit()

        response = client.post(
            f"/api/v1/workout-sessions/{session.id}/complete",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session_id"] == str(session.id)
        assert data["data"]["status"] == SessionStatusEnum.COMPLETED.value
        assert "duration_seconds" in data["data"]
        assert "new_personal_records" in data["data"]

        # Cleanup
        db.delete(session)
        db.commit()

    def test_complete_workout_session_not_found(self, client: TestClient, auth_headers: dict):
        """Test completing non-existent session."""
        fake_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/workout-sessions/{fake_id}/complete",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_complete_workout_session_already_completed(
        self,
        client: TestClient,
        auth_headers: dict,
        test_completed_workout_session: WorkoutSession,
    ):
        """Test completing already completed session."""
        response = client.post(
            f"/api/v1/workout-sessions/{test_completed_workout_session.id}/complete",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_complete_workout_session_unauthorized(
        self, client: TestClient, test_workout_session: WorkoutSession
    ):
        """Test completing session without authentication."""
        response = client.post(
            f"/api/v1/workout-sessions/{test_workout_session.id}/complete",
            json={},
        )

        assert response.status_code == 401


class TestSkipWorkoutSession:
    """Tests for POST /api/v1/workout-sessions/{session_id}/skip"""

    def test_skip_workout_session_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_workout_plan: WorkoutPlan,
        test_workout: Workout,
    ):
        """Test skipping a workout session."""
        # Create a new session to skip
        session = WorkoutSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            workout_plan_id=test_workout_plan.id,
            workout_id=test_workout.id,
            status=SessionStatusEnum.IN_PROGRESS,
        )
        db.add(session)
        db.commit()

        response = client.post(
            f"/api/v1/workout-sessions/{session.id}/skip",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session_id"] == str(session.id)
        assert data["data"]["status"] == SessionStatusEnum.ABANDONED.value

        # Cleanup
        db.delete(session)
        db.commit()

    def test_skip_workout_session_not_found(self, client: TestClient, auth_headers: dict):
        """Test skipping non-existent session."""
        fake_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/workout-sessions/{fake_id}/skip",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_skip_workout_session_not_in_progress(
        self,
        client: TestClient,
        auth_headers: dict,
        test_completed_workout_session: WorkoutSession,
    ):
        """Test skipping already completed session."""
        response = client.post(
            f"/api/v1/workout-sessions/{test_completed_workout_session.id}/skip",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_skip_workout_session_unauthorized(
        self, client: TestClient, test_workout_session: WorkoutSession
    ):
        """Test skipping session without authentication."""
        response = client.post(
            f"/api/v1/workout-sessions/{test_workout_session.id}/skip",
            json={},
        )

        assert response.status_code == 401


class TestDeleteWorkoutSession:
    """Tests for DELETE /api/v1/workout-sessions/{session_id}"""

    def test_delete_workout_session_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_workout_plan: WorkoutPlan,
        test_workout: Workout,
    ):
        """Test soft deleting a workout session."""
        # Create a session to delete
        session = WorkoutSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            workout_plan_id=test_workout_plan.id,
            workout_id=test_workout.id,
            status=SessionStatusEnum.COMPLETED,
        )
        db.add(session)
        db.commit()

        response = client.delete(f"/api/v1/workout-sessions/{session.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify it's soft deleted
        db.refresh(session)
        assert session.deleted_at is not None

        # Cleanup
        db.delete(session)
        db.commit()

    def test_delete_workout_session_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting non-existent session."""
        fake_id = uuid.uuid4()
        response = client.delete(f"/api/v1/workout-sessions/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_workout_session_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout_session: WorkoutSession,
    ):
        """Test that user cannot delete another user's session."""
        response = client.delete(
            f"/api/v1/workout-sessions/{test_workout_session.id}",
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_delete_workout_session_unauthorized(
        self, client: TestClient, test_workout_session: WorkoutSession
    ):
        """Test deleting session without authentication."""
        response = client.delete(f"/api/v1/workout-sessions/{test_workout_session.id}")

        assert response.status_code == 401
