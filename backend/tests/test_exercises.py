"""
Tests for exercises API endpoints.
"""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Equipment, Exercise, ExerciseEquipment, User, UserEquipment


class TestListExercises:
    """Tests for GET /api/v1/exercises"""

    def test_list_exercises_success(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test listing all exercises."""
        response = client.get("/api/v1/exercises", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "exercises" in data["data"]
        assert "pagination" in data["data"]
        assert isinstance(data["data"]["exercises"], list)

    def test_list_exercises_pagination(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test exercise list pagination."""
        response = client.get("/api/v1/exercises?page=1&limit=10", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        pagination = data["data"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 10
        assert "total" in pagination
        assert "total_pages" in pagination

    def test_list_exercises_search(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test searching exercises by name."""
        # Use the full unique name to avoid pagination issues
        search_term = test_exercise.name
        response = client.get(f"/api/v1/exercises?search={search_term}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should find our test exercise
        exercise_names = [ex["name"] for ex in data["data"]["exercises"]]
        assert test_exercise.name in exercise_names

    def test_list_exercises_filter_muscle_group(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test filtering exercises by muscle group."""
        muscle_group = test_exercise.primary_muscle_groups[0].value
        response = client.get(
            f"/api/v1/exercises?muscle_group={muscle_group}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # All returned exercises should have the muscle group
        for ex in data["data"]["exercises"]:
            assert muscle_group in ex["primary_muscle_groups"]

    def test_list_exercises_filter_equipment(
        self,
        client: TestClient,
        auth_headers: dict,
        test_exercise_with_equipment: Exercise,
        test_equipment: Equipment,
    ):
        """Test filtering exercises by equipment."""
        response = client.get(
            f"/api/v1/exercises?equipment_id={test_equipment.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should find our test exercise that uses this equipment
        exercise_ids = [ex["id"] for ex in data["data"]["exercises"]]
        assert str(test_exercise_with_equipment.id) in exercise_ids

    def test_list_exercises_filter_user_can_perform(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_exercise_with_equipment: Exercise,
        test_equipment: Equipment,
    ):
        """Test filtering exercises by what user can perform."""
        # Use search to find our specific test exercise (pagination workaround)
        exercise_name = test_exercise_with_equipment.name

        # First, user doesn't own equipment - should not be able to perform
        response = client.get(
            f"/api/v1/exercises?user_can_perform=true&search={exercise_name}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        exercise_ids = [ex["id"] for ex in data["data"]["exercises"]]
        # Exercise requiring equipment user doesn't have should not be listed
        assert str(test_exercise_with_equipment.id) not in exercise_ids

        # Now add equipment ownership
        user_equipment = UserEquipment(
            user_id=test_user.id,
            equipment_id=test_equipment.id,
        )
        db.add(user_equipment)
        db.commit()

        # Now user should be able to perform the exercise
        response = client.get(
            f"/api/v1/exercises?user_can_perform=true&search={exercise_name}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        exercise_ids = [ex["id"] for ex in data["data"]["exercises"]]
        assert str(test_exercise_with_equipment.id) in exercise_ids

    def test_list_exercises_limit_max(self, client: TestClient, auth_headers: dict):
        """Test that limit is capped at 100."""
        response = client.get("/api/v1/exercises?limit=200", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["pagination"]["limit"] == 100

    def test_list_exercises_unauthorized(self, client: TestClient):
        """Test listing exercises without authentication."""
        response = client.get("/api/v1/exercises")

        assert response.status_code == 401


class TestGetExercise:
    """Tests for GET /api/v1/exercises/{exercise_id}"""

    def test_get_exercise_success(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test getting exercise details."""
        response = client.get(f"/api/v1/exercises/{test_exercise.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(test_exercise.id)
        assert data["data"]["name"] == test_exercise.name
        assert "primary_muscle_groups" in data["data"]
        assert "secondary_muscle_groups" in data["data"]
        assert "equipment" in data["data"]
        assert "personal_records" in data["data"]
        assert "default_weight" in data["data"]
        assert "default_reps" in data["data"]
        assert "default_rest_time_seconds" in data["data"]

    def test_get_exercise_with_equipment(
        self,
        client: TestClient,
        auth_headers: dict,
        test_exercise_with_equipment: Exercise,
        test_equipment: Equipment,
    ):
        """Test getting exercise details includes equipment."""
        response = client.get(
            f"/api/v1/exercises/{test_exercise_with_equipment.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        equipment_ids = [eq["id"] for eq in data["data"]["equipment"]]
        assert str(test_equipment.id) in equipment_ids

    def test_get_exercise_with_personal_records(
        self,
        client: TestClient,
        auth_headers: dict,
        test_personal_record,
        test_exercise: Exercise,
    ):
        """Test getting exercise details includes personal records."""
        response = client.get(f"/api/v1/exercises/{test_exercise.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["personal_records"]) >= 1
        pr_ids = [pr["id"] for pr in data["data"]["personal_records"]]
        assert str(test_personal_record.id) in pr_ids

    def test_get_exercise_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent exercise."""
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/exercises/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_get_exercise_unauthorized(self, client: TestClient, test_exercise: Exercise):
        """Test getting exercise without authentication."""
        response = client.get(f"/api/v1/exercises/{test_exercise.id}")

        assert response.status_code == 401


class TestGetExerciseSubstitutes:
    """Tests for GET /api/v1/exercises/{exercise_id}/substitutes"""

    def test_get_substitutes_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_exercise: Exercise,
        test_exercise_2: Exercise,
    ):
        """Test getting exercise substitutes."""
        response = client.get(
            f"/api/v1/exercises/{test_exercise.id}/substitutes", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        # Each substitute should have required fields
        for sub in data["data"]:
            assert "id" in sub
            assert "name" in sub
            assert "primary_muscle_groups" in sub
            assert "secondary_muscle_groups" in sub
            assert "equipment" in sub
            assert "match_score" in sub

    def test_get_substitutes_respects_equipment(
        self,
        client: TestClient,
        auth_headers: dict,
        db: Session,
        test_user: User,
        test_exercise: Exercise,
    ):
        """Test that substitutes only include exercises user can perform."""
        # Create an exercise with equipment that user doesn't have
        equipment = Equipment(
            id=uuid.uuid4(),
            name=f"Special Equipment {uuid.uuid4().hex[:8]}",
            description="Equipment user does not have",
        )
        db.add(equipment)
        db.commit()

        exercise_with_equipment = Exercise(
            id=uuid.uuid4(),
            name=f"Special Exercise {uuid.uuid4().hex[:8]}",
            primary_muscle_groups=test_exercise.primary_muscle_groups,  # Same muscle group
            description="Exercise requiring special equipment",
        )
        db.add(exercise_with_equipment)
        db.commit()

        exercise_equipment = ExerciseEquipment(
            exercise_id=exercise_with_equipment.id,
            equipment_id=equipment.id,
        )
        db.add(exercise_equipment)
        db.commit()

        response = client.get(
            f"/api/v1/exercises/{test_exercise.id}/substitutes", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # The exercise requiring equipment user doesn't have should not be in substitutes
        substitute_ids = [sub["id"] for sub in data["data"]]
        assert str(exercise_with_equipment.id) not in substitute_ids

    def test_get_substitutes_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting substitutes for non-existent exercise."""
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/exercises/{fake_id}/substitutes", headers=auth_headers)

        assert response.status_code == 404

    def test_get_substitutes_unauthorized(self, client: TestClient, test_exercise: Exercise):
        """Test getting substitutes without authentication."""
        response = client.get(f"/api/v1/exercises/{test_exercise.id}/substitutes")

        assert response.status_code == 401

    def test_get_substitutes_sorted_by_match_score(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test that substitutes are sorted by match score descending."""
        response = client.get(
            f"/api/v1/exercises/{test_exercise.id}/substitutes", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 1:
            scores = [sub["match_score"] for sub in data["data"]]
            assert scores == sorted(scores, reverse=True)


class TestCreateCustomExercise:
    """Tests for POST /api/v1/exercises"""

    def test_create_custom_exercise_success(self, client: TestClient, auth_headers: dict):
        """Test creating a custom exercise."""
        exercise_data = {
            "name": f"My Custom Exercise {uuid.uuid4().hex[:8]}",
            "primary_muscle_groups": ["chest"],
            "secondary_muscle_groups": ["triceps"],
            "description": "A custom exercise",
            "default_reps": 10,
            "default_rest_time_seconds": 60,
        }
        response = client.post("/api/v1/exercises", json=exercise_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == exercise_data["name"]
        assert data["data"]["is_custom"] is True
        assert data["data"]["user_id"] is not None
        assert data["data"]["primary_muscle_groups"] == ["chest"]
        assert data["data"]["secondary_muscle_groups"] == ["triceps"]

    def test_create_custom_exercise_with_equipment(
        self, client: TestClient, auth_headers: dict, test_equipment: Equipment
    ):
        """Test creating a custom exercise with equipment."""
        exercise_data = {
            "name": f"Equipment Exercise {uuid.uuid4().hex[:8]}",
            "primary_muscle_groups": ["back"],
            "equipment_ids": [str(test_equipment.id)],
        }
        response = client.post("/api/v1/exercises", json=exercise_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_custom"] is True

    def test_create_custom_exercise_duplicate_name(self, client: TestClient, auth_headers: dict):
        """Test creating custom exercise with duplicate name fails."""
        exercise_data = {
            "name": f"Duplicate Test {uuid.uuid4().hex[:8]}",
            "primary_muscle_groups": ["chest"],
        }
        # Create first
        response1 = client.post("/api/v1/exercises", json=exercise_data, headers=auth_headers)
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = client.post("/api/v1/exercises", json=exercise_data, headers=auth_headers)
        assert response2.status_code == 400

    def test_create_custom_exercise_can_use_global_name(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test user can create custom exercise with same name as global exercise."""
        exercise_data = {
            "name": test_exercise.name,
            "primary_muscle_groups": ["chest"],
        }
        response = client.post("/api/v1/exercises", json=exercise_data, headers=auth_headers)

        # Should succeed since global exercise has user_id=NULL
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["is_custom"] is True

    def test_create_custom_exercise_invalid_equipment(self, client: TestClient, auth_headers: dict):
        """Test creating custom exercise with invalid equipment fails."""
        exercise_data = {
            "name": f"Invalid Equipment Exercise {uuid.uuid4().hex[:8]}",
            "primary_muscle_groups": ["chest"],
            "equipment_ids": [str(uuid.uuid4())],  # Non-existent equipment
        }
        response = client.post("/api/v1/exercises", json=exercise_data, headers=auth_headers)

        assert response.status_code == 400

    def test_create_custom_exercise_unauthorized(self, client: TestClient):
        """Test creating exercise without authentication."""
        exercise_data = {
            "name": "Unauthorized Exercise",
            "primary_muscle_groups": ["chest"],
        }
        response = client.post("/api/v1/exercises", json=exercise_data)

        assert response.status_code == 401


class TestUpdateCustomExercise:
    """Tests for PUT /api/v1/exercises/{exercise_id}"""

    def test_update_custom_exercise_success(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test updating a custom exercise."""
        # Create a custom exercise first
        exercise = Exercise(
            id=uuid.uuid4(),
            name=f"Update Test Exercise {uuid.uuid4().hex[:8]}",
            primary_muscle_groups=["chest"],
            is_custom=True,
            user_id=test_user.id,
        )
        db.add(exercise)
        db.commit()

        update_data = {
            "name": f"Updated Exercise {uuid.uuid4().hex[:8]}",
            "description": "Updated description",
        }
        response = client.put(
            f"/api/v1/exercises/{exercise.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == update_data["name"]
        assert data["data"]["description"] == update_data["description"]

    def test_update_custom_exercise_partial(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test partial update of custom exercise."""
        exercise = Exercise(
            id=uuid.uuid4(),
            name=f"Partial Update Test {uuid.uuid4().hex[:8]}",
            primary_muscle_groups=["chest"],
            description="Original description",
            is_custom=True,
            user_id=test_user.id,
        )
        db.add(exercise)
        db.commit()

        # Only update name
        update_data = {"name": f"New Name {uuid.uuid4().hex[:8]}"}
        response = client.put(
            f"/api/v1/exercises/{exercise.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Name updated
        assert data["data"]["name"] == update_data["name"]
        # Description preserved
        assert data["data"]["description"] == "Original description"

    def test_update_global_exercise_forbidden(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test updating a global exercise fails."""
        update_data = {"name": "Hacked Name"}
        response = client.put(
            f"/api/v1/exercises/{test_exercise.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 403

    def test_update_other_user_exercise_forbidden(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test updating another user's custom exercise fails."""
        # Create another user's exercise
        other_user = User(
            id=uuid.uuid4(),
            email=f"other_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="hashed_password",
        )
        db.add(other_user)
        db.commit()

        exercise = Exercise(
            id=uuid.uuid4(),
            name=f"Other User Exercise {uuid.uuid4().hex[:8]}",
            primary_muscle_groups=["chest"],
            is_custom=True,
            user_id=other_user.id,
        )
        db.add(exercise)
        db.commit()

        update_data = {"name": "Stolen Name"}
        response = client.put(
            f"/api/v1/exercises/{exercise.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 403

    def test_update_exercise_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating non-existent exercise."""
        fake_id = uuid.uuid4()
        update_data = {"name": "Ghost Exercise"}
        response = client.put(
            f"/api/v1/exercises/{fake_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_exercise_unauthorized(self, client: TestClient, test_exercise: Exercise):
        """Test updating exercise without authentication."""
        update_data = {"name": "Hacked"}
        response = client.put(f"/api/v1/exercises/{test_exercise.id}", json=update_data)

        assert response.status_code == 401


class TestDeleteCustomExercise:
    """Tests for DELETE /api/v1/exercises/{exercise_id}"""

    def test_delete_custom_exercise_success(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test deleting a custom exercise."""
        exercise = Exercise(
            id=uuid.uuid4(),
            name=f"Delete Test Exercise {uuid.uuid4().hex[:8]}",
            primary_muscle_groups=["chest"],
            is_custom=True,
            user_id=test_user.id,
        )
        db.add(exercise)
        db.commit()
        exercise_id = exercise.id

        response = client.delete(f"/api/v1/exercises/{exercise_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify deleted
        deleted = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        assert deleted is None

    def test_delete_global_exercise_forbidden(
        self, client: TestClient, auth_headers: dict, test_exercise: Exercise
    ):
        """Test deleting a global exercise fails."""
        response = client.delete(f"/api/v1/exercises/{test_exercise.id}", headers=auth_headers)

        assert response.status_code == 403

    def test_delete_other_user_exercise_forbidden(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test deleting another user's custom exercise fails."""
        other_user = User(
            id=uuid.uuid4(),
            email=f"other_delete_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="hashed_password",
        )
        db.add(other_user)
        db.commit()

        exercise = Exercise(
            id=uuid.uuid4(),
            name=f"Other Delete Exercise {uuid.uuid4().hex[:8]}",
            primary_muscle_groups=["chest"],
            is_custom=True,
            user_id=other_user.id,
        )
        db.add(exercise)
        db.commit()

        response = client.delete(f"/api/v1/exercises/{exercise.id}", headers=auth_headers)

        assert response.status_code == 403

    def test_delete_exercise_in_plan_fails(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test deleting exercise used in a plan fails."""
        from app.models import Workout, WorkoutExercise, WorkoutPlan

        # Create custom exercise
        exercise = Exercise(
            id=uuid.uuid4(),
            name=f"Plan Exercise {uuid.uuid4().hex[:8]}",
            primary_muscle_groups=["chest"],
            is_custom=True,
            user_id=test_user.id,
        )
        db.add(exercise)
        db.commit()

        # Create a plan that uses this exercise
        plan = WorkoutPlan(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Test Plan",
        )
        db.add(plan)
        db.commit()

        workout = Workout(
            id=uuid.uuid4(),
            workout_plan_id=plan.id,
            name="Day 1",
            order_index=0,
        )
        db.add(workout)
        db.commit()

        workout_exercise = WorkoutExercise(
            id=uuid.uuid4(),
            workout_id=workout.id,
            exercise_id=exercise.id,
            sequence=1,
            sets=3,
            reps_min=8,
            reps_max=12,
        )
        db.add(workout_exercise)
        db.commit()

        # Try to delete
        response = client.delete(f"/api/v1/exercises/{exercise.id}", headers=auth_headers)

        assert response.status_code == 400
        assert "used in workout plans" in response.json()["detail"].lower()

    def test_delete_exercise_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting non-existent exercise."""
        fake_id = uuid.uuid4()
        response = client.delete(f"/api/v1/exercises/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_exercise_unauthorized(self, client: TestClient, test_exercise: Exercise):
        """Test deleting exercise without authentication."""
        response = client.delete(f"/api/v1/exercises/{test_exercise.id}")

        assert response.status_code == 401


class TestCustomExercisesInList:
    """Tests for custom exercises appearing in list endpoint"""

    def test_list_includes_own_custom_exercises(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test that list includes user's custom exercises."""
        custom_name = f"My Custom List Exercise {uuid.uuid4().hex[:8]}"
        exercise = Exercise(
            id=uuid.uuid4(),
            name=custom_name,
            primary_muscle_groups=["chest"],
            is_custom=True,
            user_id=test_user.id,
        )
        db.add(exercise)
        db.commit()

        response = client.get(f"/api/v1/exercises?search={custom_name}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        exercise_names = [ex["name"] for ex in data["data"]["exercises"]]
        assert custom_name in exercise_names

    def test_list_excludes_other_user_custom_exercises(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """Test that list does not include other users' custom exercises."""
        other_user = User(
            id=uuid.uuid4(),
            email=f"other_list_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="hashed_password",
        )
        db.add(other_user)
        db.commit()

        other_custom_name = f"Other User Custom {uuid.uuid4().hex[:8]}"
        exercise = Exercise(
            id=uuid.uuid4(),
            name=other_custom_name,
            primary_muscle_groups=["chest"],
            is_custom=True,
            user_id=other_user.id,
        )
        db.add(exercise)
        db.commit()

        response = client.get(f"/api/v1/exercises?search={other_custom_name}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        exercise_names = [ex["name"] for ex in data["data"]["exercises"]]
        assert other_custom_name not in exercise_names

    def test_list_shows_is_custom_flag(
        self, client: TestClient, auth_headers: dict, db: Session, test_user: User
    ):
        """Test that list response includes is_custom flag."""
        custom_name = f"Custom Flag Test {uuid.uuid4().hex[:8]}"
        exercise = Exercise(
            id=uuid.uuid4(),
            name=custom_name,
            primary_muscle_groups=["chest"],
            is_custom=True,
            user_id=test_user.id,
        )
        db.add(exercise)
        db.commit()

        response = client.get(f"/api/v1/exercises?search={custom_name}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        custom_exercises = [ex for ex in data["data"]["exercises"] if ex["name"] == custom_name]
        assert len(custom_exercises) == 1
        assert custom_exercises[0]["is_custom"] is True
