# Workout Plan Parser - Usage Guide

## Overview

The Workout Plan Parser is an AI-powered feature that converts plain text workout plans into structured data. It uses LiteLLM as a gateway to various LLM providers (OpenAI, Anthropic, etc.) and performs fuzzy matching to map exercise names to the database.

## How It Works

### Two-Step Import Process

1. **Parse Text** (`POST /api/v1/workout-plans/parse`)
   - Submit plain text workout plan
   - AI extracts structure and exercises
   - System matches exercises to database
   - Returns parsed data with confidence scores for review

2. **Create Plan** (`POST /api/v1/workout-plans/from-parsed`)
   - User reviews and confirms/modifies parsed exercises
   - Submit confirmed data with import_log_id
   - System creates workout plan in database

## Supported Text Formats

### Basic Format
```
Exercise Name: SetsxReps
```

**Example:**
```
Bench Press: 3x8
Squat: 5x5
Deadlift: 3x5
```

### Format with Rest Times
```
Exercise Name: SetsxReps (rest Xs)
```

**Example:**
```
Bench Press: 3x8-10 (rest 90s)
Squat: 5x5 (rest 180s)
Overhead Press: 3x8-10 (rest 60s)
```

### Format with Plan Name and Description
```
Plan Name

Description or notes about the plan

Exercise Name: SetsxReps
Exercise Name: SetsxReps
```

**Example:**
```
Starting Strength

A linear progression program for beginners focusing on compound movements.

Squat: 3x5
Bench Press: 3x5
Deadlift: 1x5
```

### Format with Day Labels
```
Day 1: Upper Body

Exercise Name: SetsxReps
Exercise Name: SetsxReps

Day 2: Lower Body

Exercise Name: SetsxReps
Exercise Name: SetsxReps
```

**Example:**
```
Day 1: Push

Bench Press: 4x8
Overhead Press: 3x10
Tricep Dips: 3x12

Day 2: Pull

Barbell Row: 4x8
Pull-ups: 3x10
Bicep Curls: 3x12
```

### Format with Notes
```
Exercise Name: SetsxReps - Notes about the exercise
```

**Example:**
```
Bench Press: 3x8-10 - Pause at bottom
Squat: 5x5 - Add 5lbs each session, focus on depth
Romanian Deadlift: 3x12 - Slow tempo (3-0-1-0)
```

### Rep Ranges

The parser supports various rep formats:
- **Single number**: `3x8` → 8-8 reps
- **Range**: `3x8-12` → 8-12 reps
- **AMRAP**: `3xAMRAP` → Will be parsed and requires user review
- **Plus sets**: `3x8+` → Will be interpreted as 8+ reps

### Rest Times

Rest times can be specified in various formats:
- `90s` or `90 seconds`
- `2m` or `2 minutes`
- `1:30` (90 seconds)

## Confidence Levels

The parser assigns confidence levels to exercise matches:

### High Confidence (≥90%)
- **Green indicator** in UI
- Exact or very close match to database
- Example: "Bench Press" → "Bench Press"
- **Action**: Usually requires no review

### Medium Confidence (80-89%)
- **Yellow indicator** in UI
- Good match with minor differences
- Example: "Back Squat" → "Barbell Squat"
- **Action**: Quick review recommended

### Low Confidence (70-79%)
- **Orange indicator** in UI
- Uncertain match, alternatives provided
- Example: "Press" → could be "Bench Press" or "Overhead Press"
- **Action**: Review and select correct exercise

### Unmatched (<70%)
- **Red indicator** in UI
- No confident match found
- Example: Typo or custom exercise not in database
- **Action**: Select from alternatives or create custom exercise

## Example API Usage

### Step 1: Parse Text

**Request:**
```bash
POST /api/v1/workout-plans/parse
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "5x5 Program\n\nSquat: 5x5\nBench Press: 5x5\nBarbell Row: 5x5"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "parsed_plan": {
      "name": "5x5 Program",
      "description": null,
      "raw_text": "5x5 Program\n\nSquat: 5x5\nBench Press: 5x5\nBarbell Row: 5x5",
      "import_log_id": "123e4567-e89b-12d3-a456-426614174000",
      "exercises": [
        {
          "matched_exercise": {
            "exercise_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "exercise_name": "Barbell Squat",
            "original_text": "Squat",
            "confidence": 0.95,
            "confidence_level": "high",
            "primary_muscle_groups": ["legs"],
            "secondary_muscle_groups": ["glutes", "core"]
          },
          "original_text": "Squat",
          "sets": 5,
          "reps_min": 5,
          "reps_max": 5,
          "rest_seconds": null,
          "notes": null,
          "sequence": 0,
          "alternatives": []
        }
      ]
    },
    "total_exercises": 3,
    "high_confidence_count": 3,
    "medium_confidence_count": 0,
    "low_confidence_count": 0,
    "unmatched_count": 0
  },
  "error": null
}
```

### Step 2: Create Workout Plan

**Request:**
```bash
POST /api/v1/workout-plans/from-parsed
Authorization: Bearer <token>
Content-Type: application/json

{
  "import_log_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "5x5 Program",
  "description": "My customized 5x5 program",
  "exercises": [
    {
      "exercise_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "sequence": 0,
      "sets": 5,
      "reps_min": 5,
      "reps_max": 5,
      "rest_seconds": 180,
      "confidence_level": "high"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "name": "5x5 Program",
    "created_at": "2025-12-06T10:00:00Z"
  },
  "error": null
}
```

## Best Practices

### For Optimal Parsing

1. **Use consistent formatting**
   - Stick to one format throughout the text
   - Use clear exercise names

2. **Include exercise details**
   - Specify equipment when ambiguous (e.g., "Barbell Row" not just "Row")
   - Include primary movement pattern (e.g., "Back Squat" not just "Squat")

3. **Be explicit with parameters**
   - Include rest times when they differ from defaults
   - Specify rep ranges clearly (8-12, not 8/12)

4. **Add helpful notes**
   - Include tempo, RPE, or other important details
   - These will be preserved in the workout plan

### For Best Results

1. **Review all matches**
   - Even high-confidence matches can be wrong
   - Check muscle groups to ensure correct exercise

2. **Use alternatives when provided**
   - For low confidence matches, review alternatives
   - Select the most appropriate exercise

3. **Correct exercise names before import**
   - Fix typos in the original text
   - Use standard exercise terminology

4. **Verify sequences**
   - Ensure exercises are in correct order
   - Reorder if necessary before finalizing

## Troubleshooting

### Common Issues

**Problem**: Parser returns unmatched exercises
- **Cause**: Exercise not in database or name too different
- **Solution**: Review alternatives or create custom exercise

**Problem**: Wrong exercise matched
- **Cause**: Ambiguous exercise name
- **Solution**: Use more specific names (e.g., "DB Bench Press" instead of "Bench")

**Problem**: Rep ranges not parsed correctly
- **Cause**: Non-standard format
- **Solution**: Use format like "3x8-12" or "3x8"

**Problem**: Rest times not extracted
- **Cause**: Non-standard format or placement
- **Solution**: Use format like "(rest 90s)" after the sets/reps

**Problem**: Multiple days parsed as single workout
- **Cause**: Parser currently doesn't split by days
- **Solution**: Parse each day separately or manually split exercises

### Error Messages

**"Text must be at least 10 characters"**
- The provided text is too short to parse
- Ensure you're submitting actual workout plan text

**"Failed to parse workout plan: Invalid JSON response from LLM"**
- LLM returned malformed data
- Try again or contact support if persists

**"Import log not found"**
- The import_log_id is invalid or expired
- Re-parse the text to get a new import_log_id

**"Exercise IDs not found"**
- One or more exercise IDs in your request don't exist
- Ensure you're using exercise_id from the parse response

## Rate Limits

- **Parse endpoint**: 10 requests per hour per user
- **Create from parsed**: No specific limit (subject to general API limits)

Exceeding rate limits returns:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many parse requests. Please try again in 45 minutes."
  }
}
```

## Tips for Different Use Cases

### Copying from a PDF or Website
1. Copy text maintaining structure
2. Clean up any formatting artifacts
3. Ensure exercise names are on same line as sets/reps
4. Remove page numbers, headers, footers

### From a Coach's Program
1. Ask for plain text format if possible
2. Maintain any important notes
3. Include week/phase information in description
4. Consider splitting complex programs into multiple plans

### From Reddit/Forum Posts
1. Copy only the workout structure
2. Remove user comments and discussion
3. Keep exercise names and sets/reps
4. Add your own notes if needed

## Support

If you encounter issues:
1. Check this guide for troubleshooting
2. Review the API documentation
3. Contact support with the import_log_id for investigation
