# Workout Plan Parser - Examples

## Overview

This document provides real-world examples of workout plans and how they are parsed by the system.

## Example 1: Simple 5x5 Program

### Input Text
```
Starting Strength

A beginner linear progression program focusing on compound lifts.

Squat: 5x5
Bench Press: 5x5
Deadlift: 1x5
Overhead Press: 5x5
Barbell Row: 5x5
```

### Expected Parse Result
```json
{
  "name": "Starting Strength",
  "description": "A beginner linear progression program focusing on compound lifts.",
  "exercises": [
    {
      "original_text": "Squat",
      "sets": 5,
      "reps_min": 5,
      "reps_max": 5,
      "rest_seconds": null,
      "notes": null,
      "sequence": 0,
      "matched_exercise": {
        "exercise_name": "Barbell Squat",
        "confidence": 0.92,
        "confidence_level": "high"
      }
    },
    {
      "original_text": "Bench Press",
      "sets": 5,
      "reps_min": 5,
      "reps_max": 5,
      "rest_seconds": null,
      "notes": null,
      "sequence": 1,
      "matched_exercise": {
        "exercise_name": "Barbell Bench Press",
        "confidence": 0.98,
        "confidence_level": "high"
      }
    }
    // ... additional exercises
  ]
}
```

## Example 2: PPL with Rep Ranges

### Input Text
```
Push Pull Legs

Day 1: Push

Bench Press: 4x6-8 (rest 3min)
Overhead Press: 3x8-10 (rest 2min)
Incline Dumbbell Press: 3x10-12
Lateral Raises: 3x12-15
Tricep Pushdowns: 3x12-15

Day 2: Pull

Deadlift: 4x5
Barbell Rows: 4x8-10
Pull-ups: 3x8-12
Face Pulls: 3x15-20
Barbell Curls: 3x10-12

Day 3: Legs

Squat: 4x6-8
Romanian Deadlift: 3x8-10
Leg Press: 3x10-12
Leg Curls: 3x12-15
Calf Raises: 4x15-20
```

### Expected Parse Result
```json
{
  "name": "Push Pull Legs",
  "description": null,
  "exercises": [
    {
      "original_text": "Bench Press",
      "sets": 4,
      "reps_min": 6,
      "reps_max": 8,
      "rest_seconds": 180,
      "notes": null,
      "sequence": 0,
      "matched_exercise": {
        "exercise_name": "Barbell Bench Press",
        "confidence": 0.98,
        "confidence_level": "high"
      }
    },
    {
      "original_text": "Overhead Press",
      "sets": 3,
      "reps_min": 8,
      "reps_max": 10,
      "rest_seconds": 120,
      "notes": null,
      "sequence": 1,
      "matched_exercise": {
        "exercise_name": "Barbell Overhead Press",
        "confidence": 0.95,
        "confidence_level": "high"
      }
    }
    // ... additional exercises
  ]
}
```

## Example 3: Complex Format with Notes

### Input Text
```
nSuns 531 LP

A high-volume linear progression program with daily progression.

Monday: Bench & Overhead Press

Bench Press: 9 sets (vary reps 5,3,1,3,3,5,3,5,3+) - AMRAP on last set
Overhead Press: 8 sets (vary reps 6,5,3,5,7,4,6,8) - Volume work
Dumbbell Flies: 3x12
Tricep Extensions: 3x12

Tuesday: Squat & Sumo Deadlift

Squat: 9 sets (vary reps 5,3,1,3,3,5,3,5,3+)
Sumo Deadlift: 8 sets (vary reps 5,5,3,5,7,4,6,8)
Leg Press: 3x12
Leg Curls: 3x12
```

### Expected Parse Result
```json
{
  "name": "nSuns 531 LP",
  "description": "A high-volume linear progression program with daily progression.",
  "exercises": [
    {
      "original_text": "Bench Press",
      "sets": 9,
      "reps_min": 1,
      "reps_max": 5,
      "rest_seconds": null,
      "notes": "9 sets (vary reps 5,3,1,3,3,5,3,5,3+) - AMRAP on last set",
      "sequence": 0,
      "matched_exercise": {
        "exercise_name": "Barbell Bench Press",
        "confidence": 0.98,
        "confidence_level": "high"
      }
    },
    {
      "original_text": "Overhead Press",
      "sets": 8,
      "reps_min": 3,
      "reps_max": 8,
      "rest_seconds": null,
      "notes": "8 sets (vary reps 6,5,3,5,7,4,6,8) - Volume work",
      "sequence": 1,
      "matched_exercise": {
        "exercise_name": "Barbell Overhead Press",
        "confidence": 0.95,
        "confidence_level": "high"
      }
    }
    // ... additional exercises
  ]
}
```

## Example 4: With Tempo and RPE

### Input Text
```
Hypertrophy Program

Upper Body

Bench Press: 4x8-10 @ RPE 8 (Tempo 3-0-1-0)
Cable Rows: 4x10-12 @ RPE 7
Overhead Press: 3x10-12
Lat Pulldowns: 3x12-15 (Squeeze at bottom)
Lateral Raises: 3x15-20 @ RPE 9
Bicep Curls: 3x12-15
Tricep Extensions: 3x12-15
```

### Expected Parse Result
```json
{
  "name": "Hypertrophy Program",
  "description": null,
  "exercises": [
    {
      "original_text": "Bench Press",
      "sets": 4,
      "reps_min": 8,
      "reps_max": 10,
      "rest_seconds": null,
      "notes": "@ RPE 8 (Tempo 3-0-1-0)",
      "sequence": 0,
      "matched_exercise": {
        "exercise_name": "Barbell Bench Press",
        "confidence": 0.98,
        "confidence_level": "high"
      }
    },
    {
      "original_text": "Cable Rows",
      "sets": 4,
      "reps_min": 10,
      "reps_max": 12,
      "rest_seconds": null,
      "notes": "@ RPE 7",
      "sequence": 1,
      "matched_exercise": {
        "exercise_name": "Cable Row",
        "confidence": 0.94,
        "confidence_level": "high"
      }
    }
    // ... additional exercises
  ]
}
```

## Example 5: Ambiguous Exercise Names (Low Confidence)

### Input Text
```
Full Body Workout

Press: 3x8
Row: 3x10
Squat: 3x12
Curl: 3x15
Extension: 3x15
```

### Expected Parse Result
```json
{
  "name": "Full Body Workout",
  "description": null,
  "exercises": [
    {
      "original_text": "Press",
      "sets": 3,
      "reps_min": 8,
      "reps_max": 8,
      "rest_seconds": null,
      "notes": null,
      "sequence": 0,
      "matched_exercise": {
        "exercise_name": "Barbell Bench Press",
        "confidence": 0.72,
        "confidence_level": "low"
      },
      "alternatives": [
        {
          "exercise_name": "Barbell Overhead Press",
          "confidence": 0.71,
          "confidence_level": "low"
        },
        {
          "exercise_name": "Dumbbell Shoulder Press",
          "confidence": 0.69,
          "confidence_level": "low"
        }
      ]
    },
    {
      "original_text": "Row",
      "sets": 3,
      "reps_min": 10,
      "reps_max": 10,
      "rest_seconds": null,
      "notes": null,
      "sequence": 1,
      "matched_exercise": {
        "exercise_name": "Barbell Row",
        "confidence": 0.78,
        "confidence_level": "low"
      },
      "alternatives": [
        {
          "exercise_name": "Dumbbell Row",
          "confidence": 0.76,
          "confidence_level": "low"
        },
        {
          "exercise_name": "Cable Row",
          "confidence": 0.74,
          "confidence_level": "low"
        }
      ]
    }
    // ... additional exercises
  ]
}
```

**Note:** User should review and select correct exercises from alternatives.

## Example 6: From Reddit Post (Needs Cleanup)

### Input Text (Raw)
```
Hey guys, here's my routine:

**Upper Day**
- Bench Press: 4x5 (currently at 185lbs)
- OHP: 3x8
- Rows: 4x8
- Face Pulls: 3x15-20
- Arms superset: 3x12

**Lower Day**
Back squat 5x5 (working up to 225)
RDL 3x8-10
Leg press 3x12
Calves 4x20

Been running this for 6 weeks, great results!
```

### Cleaned Input
```
Upper Day

Bench Press: 4x5
Overhead Press: 3x8
Barbell Rows: 4x8
Face Pulls: 3x15-20
Bicep Curls: 3x12
Tricep Extensions: 3x12

Lower Day

Back Squat: 5x5
Romanian Deadlift: 3x8-10
Leg Press: 3x12
Calf Raises: 4x20
```

### Expected Parse Result
```json
{
  "name": "Workout Plan",
  "description": null,
  "exercises": [
    {
      "original_text": "Bench Press",
      "sets": 4,
      "reps_min": 5,
      "reps_max": 5,
      "matched_exercise": {
        "exercise_name": "Barbell Bench Press",
        "confidence": 0.98,
        "confidence_level": "high"
      }
    }
    // ... additional exercises
  ]
}
```

## Example 7: Bodyweight Program

### Input Text
```
Bodyweight Home Workout

Push Day:
Push-ups: 4xAMRAP (rest 90s)
Pike Push-ups: 3x10-12
Diamond Push-ups: 3x8-10
Dips: 3xAMRAP
Plank: 3x60s

Pull Day:
Pull-ups: 5xAMRAP (rest 2min)
Chin-ups: 3xAMRAP
Inverted Rows: 3x10-12
Hanging Leg Raises: 3x10-15
```

### Expected Parse Result
```json
{
  "name": "Bodyweight Home Workout",
  "description": null,
  "exercises": [
    {
      "original_text": "Push-ups",
      "sets": 4,
      "reps_min": 1,
      "reps_max": 50,
      "rest_seconds": 90,
      "notes": "AMRAP",
      "sequence": 0,
      "matched_exercise": {
        "exercise_name": "Push-up",
        "confidence": 0.96,
        "confidence_level": "high"
      }
    },
    {
      "original_text": "Pike Push-ups",
      "sets": 3,
      "reps_min": 10,
      "reps_max": 12,
      "rest_seconds": null,
      "notes": null,
      "sequence": 1,
      "matched_exercise": {
        "exercise_name": "Pike Push-up",
        "confidence": 0.94,
        "confidence_level": "high"
      }
    }
    // ... additional exercises
  ]
}
```

## Example 8: Powerlifting Peaking Program

### Input Text
```
12 Week Peaking Program - Week 10

Monday - Squat Day
Squat: 1x3 @ 90%, 2x2 @ 95% (rest 5min)
Pause Squat: 3x3 @ 75% (2s pause)
Front Squat: 3x5 @ 70%
Leg Curls: 3x10

Wednesday - Bench Day
Bench Press: 1x3 @ 90%, 2x2 @ 95%
Close Grip Bench: 3x5 @ 75%
Incline Press: 3x8
Barbell Rows: 4x8

Friday - Deadlift Day
Deadlift: 1x3 @ 90%, 2x2 @ 95%
Deficit Deadlift: 3x3 @ 75% (2" deficit)
Romanian Deadlift: 3x6
Good Mornings: 3x10
```

### Expected Parse Result
```json
{
  "name": "12 Week Peaking Program - Week 10",
  "description": null,
  "exercises": [
    {
      "original_text": "Squat",
      "sets": 3,
      "reps_min": 2,
      "reps_max": 3,
      "rest_seconds": 300,
      "notes": "1x3 @ 90%, 2x2 @ 95%",
      "sequence": 0,
      "matched_exercise": {
        "exercise_name": "Barbell Squat",
        "confidence": 0.95,
        "confidence_level": "high"
      }
    },
    {
      "original_text": "Pause Squat",
      "sets": 3,
      "reps_min": 3,
      "reps_max": 3,
      "rest_seconds": null,
      "notes": "3x3 @ 75% (2s pause)",
      "sequence": 1,
      "matched_exercise": {
        "exercise_name": "Pause Squat",
        "confidence": 0.92,
        "confidence_level": "high"
      }
    }
    // ... additional exercises
  ]
}
```

## Tips for Each Example Type

### Simple Programs (Example 1)
- Clean, straightforward format
- High confidence matches expected
- Minimal user review needed

### Rep Range Programs (Example 2)
- System correctly parses min/max reps
- Rest times extracted from parentheses
- Day labels preserved in notes/description

### Complex Programs (Example 3)
- Detailed notes captured
- Varying rep schemes handled
- May require user to adjust rep ranges

### Tempo/RPE Programs (Example 4)
- Tempo and RPE captured in notes
- User can reference during workouts
- Consider adding tempo/RPE fields in future

### Ambiguous Names (Example 5)
- Low confidence triggers alternative suggestions
- User must review and select correct exercise
- Consider renaming to be more specific

### Reddit/Forum Posts (Example 6)
- Clean up before parsing
- Remove commentary and personal notes
- Extract only workout structure

### Bodyweight Programs (Example 7)
- AMRAP handled as rep range
- Time-based exercises (planks) may need adjustment
- Equipment requirements clear

### Percentage-Based Programs (Example 8)
- Percentages captured in notes
- Complex rep schemes simplified
- User should reference notes for exact protocol

## Common Parsing Patterns

### Pattern: "Exercise: SetsxReps"
```
Bench Press: 3x8
→ Exercise: Bench Press, Sets: 3, Reps: 8-8
```

### Pattern: "Exercise: SetsxMin-Max"
```
Bench Press: 3x8-10
→ Exercise: Bench Press, Sets: 3, Reps: 8-10
```

### Pattern: "Exercise: SetsxReps (rest Xs)"
```
Bench Press: 3x8 (rest 90s)
→ Exercise: Bench Press, Sets: 3, Reps: 8-8, Rest: 90s
```

### Pattern: "Exercise: SetsxReps @ RPE X"
```
Bench Press: 3x8 @ RPE 8
→ Exercise: Bench Press, Sets: 3, Reps: 8-8, Notes: "@ RPE 8"
```

### Pattern: "Exercise: SetsxReps - Notes"
```
Bench Press: 3x8 - Pause at bottom
→ Exercise: Bench Press, Sets: 3, Reps: 8-8, Notes: "Pause at bottom"
```

## Handling Edge Cases

### Missing Information
- **No plan name**: Defaults to "Workout Plan"
- **No rest time**: Defaults to null (uses exercise defaults)
- **No description**: Set to null

### Special Rep Schemes
- **AMRAP**: Parsed as wide rep range (1-50)
- **To failure**: Captured in notes
- **Drop sets**: Captured in notes
- **Cluster sets**: May require manual adjustment

### Time-Based Exercises
- **Planks (60s)**: Parsed as 1 rep, time in notes
- **Interval training**: Captured in notes
- **Timed holds**: May need custom handling

## Testing Your Parsing

Use these examples to test the parser:

1. Copy input text
2. Call `/api/v1/workout-plans/parse`
3. Compare result to expected output
4. Check confidence levels
5. Verify exercise matches
6. Review alternatives for low confidence

Report any discrepancies or unexpected behavior for continuous improvement.
