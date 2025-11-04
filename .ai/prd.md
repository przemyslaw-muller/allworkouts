# Product Requirements Document (PRD) - AllWorkouts

## 1. Product Overview
AllWorkouts is a web application that helps users manage and track their strength training programs. The application's core functionality allows users to import text-based workout plans through AI-powered parsing and track their training progress over time.

The MVP focuses on three key capabilities:
1. Converting text-based workout plans into structured data
2. Logging workout performance
3. Tracking training history

## 2. User Problem
Strength training enthusiasts face several challenges when following workout programs:
- Manual entry of workout plans is time-consuming and error-prone
- Tracking progress across multiple exercises is difficult
- Managing equipment requirements and availability is complex
- Recording workout history in a structured way is cumbersome

AllWorkouts solves these problems by providing automated plan import, structured logging, and simple progress tracking.

## 3. Functional Requirements

### 3.1 User Authentication
- Email-based user authentication
- Unit preference selection during first login (kg/cm or lbs/inches)
- Equipment availability selection in user profile (and unit preference as well)

### 3.2 Workout Plan Management
- AI-powered parsing of plain text workout plans
- Exercise matching against database (80%+ confidence threshold)
- Three-state confidence system for matches (high, medium, low)
- Exercise database with main and secondary muscle groups, default values for rest times and equipment
- Basic CRUD operations for workout plans
- Equipment compatibility verification

### 3.3 Workout Logging
- Recording of sets, reps, and weights for each exercise
- Rest timer after logging a set
- Display of previous workout values during logging
- Tracking of three PR types:
  - One Rep Max (1RM)
  - Set volume (weight × reps)
  - Total volume (weight × total reps)
- All sets must be logged to mark the workout session as completed, otherwise it will be marked as incomplete

### 3.4 History Tracking
- Chronological list of completed workouts
- Basic filtering by completion status and workout name
- Detailed view of individual workout sessions
- Performance metrics tracking

## 4. Product Boundaries

### 4.1 MVP Scope
- Web application only
- Plain text workout plan import
- Basic CRUD operations
- Exercise substitution recommendations on the Edit Workout screen
- Essential progress tracking

### 4.2 Out of Scope
- Mobile application
- Offline mode
- Social features
- Advanced analytics and progress charts
- AI-generated workout plans
- Warm-up set tracking
- Supersets/circuit training support

## 5. User Stories

### Authentication
US-001: User Registration
- As a new user, I want to create an account
- Acceptance Criteria:
  - User can register with email
  - User must select preferred units (kg/cm or lbs/inches)
  - User must select available equipment

US-002: User Login
- As a registered user, I want to access my account
- Acceptance Criteria:
  - User can log in with email credentials
  - User is directed to their dashboard after login

### Equipment Management
US-003: Equipment Setup
- As a user, I want to specify my available equipment
- Acceptance Criteria:
  - User can select from equipment database
  - User can update equipment list at any time
  - System shows equipment requirements for workouts

### Plan Management
US-004: Workout Plan Import
- As a user, I want to import a text-based workout plan
- Acceptance Criteria:
  - User can paste plain text
  - System identifies exercises, sets, reps, rest times with confidence levels
  - User can verify and edit matched exercises
  - System validates equipment compatibility

US-005: Workout Plan Editing
- As a user, I want to edit my workout plans
- Acceptance Criteria:
  - User can modify exercise selection
  - System shows suggestions for equivalent exercises (by muscle groups) matching the user's equipment
  - User can adjust sets, reps, and rest times
  - User can rename workout plans
  - System maintains exercise database references

### Workout Logging
US-006: Session Logging
- As a user, I want to log my workout performance
- Acceptance Criteria:
  - System displays previous session values
  - System shows PR records
  - System pre-fills weight and reps for each set from previous log or exercise defaults
  - User can log weight and reps for each set
  - All sets must be logged for completion (but incomplete workouts can be saved as well)

US-007: Progress Review
- As a user, I want to view my workout history
- Acceptance Criteria:
  - User can view chronological list of workouts
  - User can see completion status
  - User can access detailed session information
  - System displays key metrics

## 6. Success Metrics

### 6.1 Import Success
- 80%+ AI parsing confidence threshold
- User verification without modifications
- Successful equipment compatibility validation

### 6.2 User Engagement
- Successful workout plan imports
- Complete workout logging rate
- Regular session logging frequency

### 6.3 System Reliability
- Accurate PR calculations
- Consistent workout history tracking
- Reliable exercise matching

### 6.4 Key Performance Indicators
- Number of successful imports
- Workout completion rate
- Exercise matching accuracy
- Session logging frequency
