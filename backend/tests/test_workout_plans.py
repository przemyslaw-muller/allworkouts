"""
Tests for workout plans API endpoints.
"""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import ConfidenceLevelEnum
from app.models import Exercise, User, Workout, WorkoutExercise, WorkoutPlan


class TestListWorkoutPlans:
    """Tests for GET /api/v1/workout-plans"""

    def test_list_workout_plans_success(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        """Test listing workout plans."""
        response = client.get("/api/v1/workout-plans", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "plans" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["plans"]) >= 1

    def test_list_workout_plans_pagination(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        """Test workout plans pagination."""
        response = client.get("/api/v1/workout-plans?page=1&limit=5", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 5

    def test_list_workout_plans_empty(self, client: TestClient, auth_headers_user2: dict):
        """Test listing workout plans when user has none."""
        response = client.get("/api/v1/workout-plans", headers=auth_headers_user2)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["plans"]) == 0

    def test_list_workout_plans_with_exercise_count(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_plan_with_exercises: WorkoutPlan,
    ):
        """Test that workout plans include exercise count."""
        response = client.get("/api/v1/workout-plans", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        plan = next(
            (
                p
                for p in data["data"]["plans"]
                if p["id"] == str(test_workout_plan_with_exercises.id)
            ),
            None,
        )
        assert plan is not None
        assert plan["exercise_count"] >= 2

    def test_list_workout_plans_unauthorized(self, client: TestClient):
        """Test listing workout plans without authentication."""
        response = client.get("/api/v1/workout-plans")

        assert response.status_code == 401


class TestGetWorkoutPlan:
    """Tests for GET /api/v1/workout-plans/{plan_id}"""

    def test_get_workout_plan_success(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        """Test getting workout plan details."""
        response = client.get(f"/api/v1/workout-plans/{test_workout_plan.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(test_workout_plan.id)
        assert data["data"]["name"] == test_workout_plan.name
        assert "workouts" in data["data"]
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]

    def test_get_workout_plan_with_exercises(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_plan_with_exercises: WorkoutPlan,
    ):
        """Test getting workout plan details includes workouts and exercises."""
        response = client.get(
            f"/api/v1/workout-plans/{test_workout_plan_with_exercises.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["workouts"]) >= 1

        # Check workout details
        workout = data["data"]["workouts"][0]
        assert "id" in workout
        assert "name" in workout
        assert "exercises" in workout
        assert len(workout["exercises"]) >= 2

        # Check exercise details within workout
        for exercise in workout["exercises"]:
            assert "id" in exercise
            assert "exercise" in exercise
            assert "sequence" in exercise
            assert "set_configurations" in exercise
            assert isinstance(exercise["set_configurations"], list)
            assert len(exercise["set_configurations"]) > 0

    def test_get_workout_plan_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent workout plan."""
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/workout-plans/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_get_workout_plan_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout_plan: WorkoutPlan,
    ):
        """Test that user cannot access another user's workout plan."""
        response = client.get(
            f"/api/v1/workout-plans/{test_workout_plan.id}",
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_get_workout_plan_unauthorized(
        self, client: TestClient, test_workout_plan: WorkoutPlan
    ):
        """Test getting workout plan without authentication."""
        response = client.get(f"/api/v1/workout-plans/{test_workout_plan.id}")

        assert response.status_code == 401


class TestCreateWorkoutPlan:
    """Tests for POST /api/v1/workout-plans"""

    def test_create_workout_plan_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_exercise: Exercise,
        test_exercise_2: Exercise,
    ):
        """Test creating a new workout plan with nested workouts."""
        response = client.post(
            "/api/v1/workout-plans",
            json={
                "name": "Test Created Plan",
                "description": "A test workout plan",
                "workouts": [
                    {
                        "name": "Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(test_exercise.id),
                                "sequence": 1,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 3, "reps_min": 8, "reps_max": 12}
                                ],
                                "rest_time_seconds": 90,
                                "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                            },
                            {
                                "exercise_id": str(test_exercise_2.id),
                                "sequence": 2,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 6, "reps_max": 10},
                                    {"set_number": 2, "reps_min": 6, "reps_max": 10},
                                    {"set_number": 3, "reps_min": 6, "reps_max": 10},
                                    {"set_number": 4, "reps_min": 6, "reps_max": 10}
                                ],
                                "rest_time_seconds": 120,
                                "confidence_level": ConfidenceLevelEnum.HIGH.value,
                            },
                        ],
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Created Plan"
        assert "id" in data["data"]

        # Cleanup
        plan_id = data["data"]["id"]
        workouts = db.query(Workout).filter(Workout.workout_plan_id == plan_id).all()
        for workout in workouts:
            db.query(WorkoutExercise).filter(WorkoutExercise.workout_id == workout.id).delete()
        db.query(Workout).filter(Workout.workout_plan_id == plan_id).delete()
        db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).delete()
        db.commit()

    def test_create_workout_plan_invalid_exercise(self, client: TestClient, auth_headers: dict):
        """Test creating workout plan with non-existent exercise."""
        fake_id = uuid.uuid4()
        response = client.post(
            "/api/v1/workout-plans",
            json={
                "name": "Invalid Plan",
                "workouts": [
                    {
                        "name": "Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(fake_id),
                                "sequence": 1,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 3, "reps_min": 8, "reps_max": 12}
                                ],
                                "rest_time_seconds": 90,
                                "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                            },
                        ],
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_workout_plan_unauthorized(self, client: TestClient, test_exercise: Exercise):
        """Test creating workout plan without authentication."""
        response = client.post(
            "/api/v1/workout-plans",
            json={
                "name": "Test Plan",
                "workouts": [
                    {
                        "name": "Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(test_exercise.id),
                                "sequence": 1,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 3, "reps_min": 8, "reps_max": 12}
                                ],
                                "rest_time_seconds": 90,
                                "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                            },
                        ],
                    },
                ],
            },
        )

        assert response.status_code == 401


class TestUpdateWorkoutPlan:
    """Tests for PUT /api/v1/workout-plans/{plan_id}"""

    def test_update_workout_plan_name(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        """Test updating workout plan name."""
        response = client.put(
            f"/api/v1/workout-plans/{test_workout_plan.id}",
            json={"name": "Updated Plan Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "updated_at" in data["data"]

    def test_update_workout_plan_description(
        self, client: TestClient, auth_headers: dict, test_workout_plan: WorkoutPlan
    ):
        """Test updating workout plan description."""
        response = client.put(
            f"/api/v1/workout-plans/{test_workout_plan.id}",
            json={"description": "Updated description"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_update_workout_plan_exercises(
        self,
        client: TestClient,
        auth_headers: dict,
        test_workout_plan: WorkoutPlan,
        test_exercise: Exercise,
    ):
        """Test updating workout plan with new workouts structure."""
        response = client.put(
            f"/api/v1/workout-plans/{test_workout_plan.id}",
            json={
                "workouts": [
                    {
                        "name": "New Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(test_exercise.id),
                                "sequence": 1,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 5, "reps_max": 5},
                                    {"set_number": 2, "reps_min": 5, "reps_max": 5},
                                    {"set_number": 3, "reps_min": 5, "reps_max": 5},
                                    {"set_number": 4, "reps_min": 5, "reps_max": 5},
                                    {"set_number": 5, "reps_min": 5, "reps_max": 5}
                                ],
                                "rest_time_seconds": 180,
                                "confidence_level": ConfidenceLevelEnum.HIGH.value,
                            },
                        ],
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_update_workout_plan_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating non-existent workout plan."""
        fake_id = uuid.uuid4()
        response = client.put(
            f"/api/v1/workout-plans/{fake_id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_workout_plan_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout_plan: WorkoutPlan,
    ):
        """Test that user cannot update another user's workout plan."""
        response = client.put(
            f"/api/v1/workout-plans/{test_workout_plan.id}",
            json={"name": "Hacked Name"},
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_update_workout_plan_unauthorized(
        self, client: TestClient, test_workout_plan: WorkoutPlan
    ):
        """Test updating workout plan without authentication."""
        response = client.put(
            f"/api/v1/workout-plans/{test_workout_plan.id}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 401


class TestDeleteWorkoutPlan:
    """Tests for DELETE /api/v1/workout-plans/{plan_id}"""

    def test_delete_workout_plan_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
    ):
        """Test soft deleting a workout plan."""
        # Create a plan to delete
        plan = WorkoutPlan(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Plan to Delete",
        )
        db.add(plan)
        db.commit()

        response = client.delete(f"/api/v1/workout-plans/{plan.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify it's soft deleted (still exists but with deleted_at)
        db.refresh(plan)
        assert plan.deleted_at is not None

        # Cleanup
        db.delete(plan)
        db.commit()

    def test_delete_workout_plan_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting non-existent workout plan."""
        fake_id = uuid.uuid4()
        response = client.delete(f"/api/v1/workout-plans/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_workout_plan_other_user(
        self,
        client: TestClient,
        auth_headers_user2: dict,
        test_workout_plan: WorkoutPlan,
    ):
        """Test that user cannot delete another user's workout plan."""
        response = client.delete(
            f"/api/v1/workout-plans/{test_workout_plan.id}",
            headers=auth_headers_user2,
        )

        assert response.status_code == 404

    def test_delete_workout_plan_unauthorized(
        self, client: TestClient, test_workout_plan: WorkoutPlan
    ):
        """Test deleting workout plan without authentication."""
        response = client.delete(f"/api/v1/workout-plans/{test_workout_plan.id}")

        assert response.status_code == 401


class TestParseWorkoutPlan:
    """Tests for POST /api/v1/workout-plans/parse"""

    def test_parse_workout_plan_success(self, client: TestClient, auth_headers: dict, db: Session):
        """Test parsing workout plan text with mocked LLM."""
        from unittest.mock import AsyncMock, patch

        # Mock LLM response - now using nested workouts structure
        mock_llm_response = {
            "name": "Test 5x5 Program",
            "description": "Strength training program",
            "workouts": [
                {
                    "name": "Day 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Squat",
                            "sets": [
                                {"reps_min": 5, "reps_max": 5},
                                {"reps_min": 5, "reps_max": 5},
                                {"reps_min": 5, "reps_max": 5},
                                {"reps_min": 5, "reps_max": 5},
                                {"reps_min": 5, "reps_max": 5}
                            ],
                            "rest_seconds": 180,
                            "notes": None,
                            "sequence": 0,
                        },
                        {
                            "original_text": "Bench Press",
                            "sets": [
                                {"reps_min": 5, "reps_max": 5},
                                {"reps_min": 5, "reps_max": 5},
                                {"reps_min": 5, "reps_max": 5},
                                {"reps_min": 5, "reps_max": 5},
                                {"reps_min": 5, "reps_max": 5}
                            ],
                            "rest_seconds": 180,
                            "notes": None,
                            "sequence": 1,
                        },
                    ],
                },
            ],
        }

        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=mock_llm_response),
        ):
            response = client.post(
                "/api/v1/workout-plans/parse",
                json={"text": "5x5 Program\nSquat 5x5\nBench Press 5x5"},
                headers=auth_headers,
            )

        # Now returns 202 with import_log_id for async processing
        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "import_log_id" in data["data"]
        import_log_id = data["data"]["import_log_id"]

        # Give async task time to complete and check the import log
        import time
        time.sleep(0.5)
        
        from app.models import WorkoutImportLog
        import_log = db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).first()
        assert import_log is not None
        assert import_log.status == "completed"
        assert import_log.result is not None
        result = import_log.result
        assert result["parsed_plan"]["name"] == "Test 5x5 Program"
        assert result["total_exercises"] == 2

        # Cleanup
        db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).delete()
        db.commit()

    def test_parse_workout_plan_with_confidence_stats(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test that parse returns confidence statistics."""
        from unittest.mock import AsyncMock, patch

        mock_llm_response = {
            "name": "Workout",
            "description": None,
            "workouts": [
                {
                    "name": "Workout 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Unknown Exercise XYZ",
                            "sets": [
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12}
                            ],
                            "rest_seconds": 90,
                            "notes": None,
                            "sequence": 0,
                        },
                    ],
                },
            ],
        }

        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=mock_llm_response),
        ):
            response = client.post(
                "/api/v1/workout-plans/parse",
                json={"text": "Workout\nUnknown Exercise XYZ 3x8-12"},
                headers=auth_headers,
            )

        # Now returns 202 with import_log_id for async processing
        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "import_log_id" in data["data"]
        import_log_id = data["data"]["import_log_id"]

        # Give async task time to complete and check the import log
        import time
        time.sleep(0.5)
        
        from app.models import WorkoutImportLog
        import_log = db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).first()
        assert import_log is not None
        assert import_log.status == "completed"
        assert import_log.result is not None
        result = import_log.result
        assert "high_confidence_count" in result
        assert "medium_confidence_count" in result
        assert "low_confidence_count" in result
        assert "unmatched_count" in result

        # Cleanup
        db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).delete()
        db.commit()

    def test_parse_workout_plan_text_too_short(self, client: TestClient, auth_headers: dict):
        """Test validation for text that is too short."""
        response = client.post(
            "/api/v1/workout-plans/parse",
            json={"text": "short"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_parse_workout_plan_unauthorized(self, client: TestClient):
        """Test parsing without authentication."""
        response = client.post(
            "/api/v1/workout-plans/parse",
            json={"text": "5x5 Program\nSquat 5x5\nBench Press 5x5"},
        )

        assert response.status_code == 401


class TestCreateWorkoutPlanFromParsed:
    """Tests for POST /api/v1/workout-plans/from-parsed"""

    def test_create_from_parsed_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_exercise: Exercise,
        test_exercise_2: Exercise,
    ):
        """Test creating workout plan from parsed data."""
        from unittest.mock import AsyncMock, patch

        # First, create an import log via parse endpoint
        mock_llm_response = {
            "name": "Parsed Program",
            "description": "From parsed data",
            "workouts": [
                {
                    "name": "Workout 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Exercise 1",
                            "sets": [
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12}
                            ],
                            "rest_seconds": 90,
                            "notes": None,
                            "sequence": 0,
                        },
                    ],
                },
            ],
        }

        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=mock_llm_response),
        ):
            parse_response = client.post(
                "/api/v1/workout-plans/parse",
                json={"text": "Parsed Program\nExercise 1 3x8-12"},
                headers=auth_headers,
            )

        assert parse_response.status_code == 202
        import_log_id = parse_response.json()["data"]["import_log_id"]
        
        # Wait for async processing
        import time
        time.sleep(0.5)

        # Now create workout plan from parsed data with nested workouts
        response = client.post(
            "/api/v1/workout-plans/from-parsed",
            json={
                "import_log_id": import_log_id,
                "name": "My Workout Plan",
                "description": "Created from parsed text",
                "workouts": [
                    {
                        "name": "Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(test_exercise.id),
                                "sequence": 0,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 3, "reps_min": 8, "reps_max": 12}
                                ],
                                "rest_time_seconds": 90,
                                "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                            },
                            {
                                "exercise_id": str(test_exercise_2.id),
                                "sequence": 1,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 6, "reps_max": 10},
                                    {"set_number": 2, "reps_min": 6, "reps_max": 10},
                                    {"set_number": 3, "reps_min": 6, "reps_max": 10},
                                    {"set_number": 4, "reps_min": 6, "reps_max": 10}
                                ],
                                "rest_time_seconds": 120,
                                "confidence_level": ConfidenceLevelEnum.HIGH.value,
                            },
                        ],
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "My Workout Plan"
        assert "id" in data["data"]

        # Verify import log was linked to the plan
        from app.models import WorkoutImportLog

        import_log = db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).first()
        assert import_log.workout_plan_id == uuid.UUID(data["data"]["id"])

        # Cleanup
        plan_id = data["data"]["id"]
        workouts = db.query(Workout).filter(Workout.workout_plan_id == plan_id).all()
        for workout in workouts:
            db.query(WorkoutExercise).filter(WorkoutExercise.workout_id == workout.id).delete()
        db.query(Workout).filter(Workout.workout_plan_id == plan_id).delete()
        db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).delete()
        db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).delete()
        db.commit()

    def test_create_from_parsed_import_log_not_found(
        self,
        client: TestClient,
        auth_headers: dict,
        test_exercise: Exercise,
    ):
        """Test creating from non-existent import log."""
        fake_id = uuid.uuid4()
        response = client.post(
            "/api/v1/workout-plans/from-parsed",
            json={
                "import_log_id": str(fake_id),
                "name": "Test Plan",
                "workouts": [
                    {
                        "name": "Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(test_exercise.id),
                                "sequence": 0,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 3, "reps_min": 8, "reps_max": 12}
                                ],
                                "rest_time_seconds": 90,
                                "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                            },
                        ],
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "Import log not found" in response.json()["detail"]

    def test_create_from_parsed_already_used(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_exercise: Exercise,
    ):
        """Test that import log cannot be used twice."""
        from unittest.mock import AsyncMock, patch

        mock_llm_response = {
            "name": "Program",
            "description": None,
            "workouts": [
                {
                    "name": "Workout 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Exercise",
                            "sets": [
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12}
                            ],
                            "rest_seconds": 90,
                            "notes": None,
                            "sequence": 0,
                        },
                    ],
                },
            ],
        }

        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=mock_llm_response),
        ):
            parse_response = client.post(
                "/api/v1/workout-plans/parse",
                json={"text": "Program\nExercise 3x8-12"},
                headers=auth_headers,
            )

        assert parse_response.status_code == 202
        import_log_id = parse_response.json()["data"]["import_log_id"]
        
        # Wait for async processing
        import time
        time.sleep(0.5)

        # Create first plan
        create_request = {
            "import_log_id": import_log_id,
            "name": "First Plan",
            "workouts": [
                {
                    "name": "Day 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "exercise_id": str(test_exercise.id),
                            "sequence": 0,
                            "set_configurations": [
                                {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                {"set_number": 3, "reps_min": 8, "reps_max": 12}
                            ],
                            "rest_time_seconds": 90,
                            "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                        },
                    ],
                },
            ],
        }

        first_response = client.post(
            "/api/v1/workout-plans/from-parsed",
            json=create_request,
            headers=auth_headers,
        )
        assert first_response.status_code == 201
        first_plan_id = first_response.json()["data"]["id"]

        # Try to create second plan with same import log
        create_request["name"] = "Second Plan"
        second_response = client.post(
            "/api/v1/workout-plans/from-parsed",
            json=create_request,
            headers=auth_headers,
        )

        assert second_response.status_code == 400
        assert "already created" in second_response.json()["detail"]

        # Cleanup
        from app.models import WorkoutImportLog

        workouts = db.query(Workout).filter(Workout.workout_plan_id == first_plan_id).all()
        for workout in workouts:
            db.query(WorkoutExercise).filter(WorkoutExercise.workout_id == workout.id).delete()
        db.query(Workout).filter(Workout.workout_plan_id == first_plan_id).delete()
        db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).delete()
        db.query(WorkoutPlan).filter(WorkoutPlan.id == first_plan_id).delete()
        db.commit()

    def test_create_from_parsed_invalid_exercise(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
    ):
        """Test creating with non-existent exercise ID."""
        from unittest.mock import AsyncMock, patch

        mock_llm_response = {
            "name": "Program",
            "description": None,
            "workouts": [
                {
                    "name": "Workout 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Exercise",
                            "sets": [
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12}
                            ],
                            "rest_seconds": 90,
                            "notes": None,
                            "sequence": 0,
                        },
                    ],
                },
            ],
        }

        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=mock_llm_response),
        ):
            parse_response = client.post(
                "/api/v1/workout-plans/parse",
                json={"text": "Program\nExercise 3x8-12"},
                headers=auth_headers,
            )

        assert parse_response.status_code == 202
        import_log_id = parse_response.json()["data"]["import_log_id"]
        
        # Wait for async processing
        import time
        time.sleep(0.5)
        fake_exercise_id = uuid.uuid4()

        response = client.post(
            "/api/v1/workout-plans/from-parsed",
            json={
                "import_log_id": import_log_id,
                "name": "Test Plan",
                "workouts": [
                    {
                        "name": "Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(fake_exercise_id),
                                "sequence": 0,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 3, "reps_min": 8, "reps_max": 12}
                                ],
                                "rest_time_seconds": 90,
                                "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                            },
                        ],
                    },
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

        # Cleanup import log
        from app.models import WorkoutImportLog

        db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).delete()
        db.commit()

    def test_create_from_parsed_unauthorized(self, client: TestClient, test_exercise: Exercise):
        """Test creating from parsed without authentication."""
        fake_id = uuid.uuid4()
        response = client.post(
            "/api/v1/workout-plans/from-parsed",
            json={
                "import_log_id": str(fake_id),
                "name": "Test Plan",
                "workouts": [
                    {
                        "name": "Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(test_exercise.id),
                                "sequence": 0,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 3, "reps_min": 8, "reps_max": 12}
                                ],
                                "rest_time_seconds": 90,
                                "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                            },
                        ],
                    },
                ],
            },
        )

        assert response.status_code == 401

    def test_create_from_parsed_other_user_import_log(
        self,
        client: TestClient,
        auth_headers: dict,
        auth_headers_user2: dict,
        db: Session,
        test_user: User,
        test_exercise: Exercise,
    ):
        """Test that user cannot use another user's import log."""
        from unittest.mock import AsyncMock, patch

        mock_llm_response = {
            "name": "Program",
            "description": None,
            "workouts": [
                {
                    "name": "Workout 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Exercise",
                            "sets": [
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12},
                                {"reps_min": 8, "reps_max": 12}
                            ],
                            "rest_seconds": 90,
                            "notes": None,
                            "sequence": 0,
                        },
                    ],
                },
            ],
        }

        # User 1 creates import log
        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=mock_llm_response),
        ):
            parse_response = client.post(
                "/api/v1/workout-plans/parse",
                json={"text": "Program\nExercise 3x8-12"},
                headers=auth_headers,
            )

        assert parse_response.status_code == 202
        import_log_id = parse_response.json()["data"]["import_log_id"]
        
        # Wait for async processing
        import time
        time.sleep(0.5)

        # User 2 tries to use it
        response = client.post(
            "/api/v1/workout-plans/from-parsed",
            json={
                "import_log_id": import_log_id,
                "name": "Stolen Plan",
                "workouts": [
                    {
                        "name": "Day 1",
                        "day_number": 1,
                        "order_index": 0,
                        "exercises": [
                            {
                                "exercise_id": str(test_exercise.id),
                                "sequence": 0,
                                "set_configurations": [
                                    {"set_number": 1, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 2, "reps_min": 8, "reps_max": 12},
                                    {"set_number": 3, "reps_min": 8, "reps_max": 12}
                                ],
                                "rest_time_seconds": 90,
                                "confidence_level": ConfidenceLevelEnum.MEDIUM.value,
                            },
                        ],
                    },
                ],
            },
            headers=auth_headers_user2,
        )

        assert response.status_code == 404
        assert "Import log not found" in response.json()["detail"]

        # Cleanup
        from app.models import WorkoutImportLog

        db.query(WorkoutImportLog).filter(WorkoutImportLog.id == import_log_id).delete()
        db.commit()
