/**
 * Common TypeScript types for AllWorkouts frontend.
 * These types mirror the backend Pydantic schemas.
 */

// ============================================================================
// Enums
// ============================================================================

export type MuscleGroup =
  | 'chest'
  | 'back'
  | 'shoulders'
  | 'biceps'
  | 'triceps'
  | 'forearms'
  | 'legs'
  | 'glutes'
  | 'core'
  | 'traps'
  | 'lats'

export type UnitSystem = 'metric' | 'imperial'

export type ConfidenceLevel = 'high' | 'medium' | 'low'

export type SessionStatus = 'in_progress' | 'completed' | 'abandoned'

export type RecordType = '1rm' | 'set_volume' | 'total_volume'

// ============================================================================
// Base Types
// ============================================================================

export interface ErrorDetail {
  code: string
  message: string
}

export interface APIResponse<T> {
  success: boolean
  data: T | null
  error: ErrorDetail | null
}

export interface PaginationInfo {
  page: number
  limit: number
  total: number
  total_pages: number
}

// ============================================================================
// Auth Types
// ============================================================================

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name?: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface AuthUser {
  id: string
  email: string
  name: string | null
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
}

export interface AuthResponse {
  user: AuthUser
  access_token: string
  refresh_token: string
}

export interface RefreshResponse {
  access_token: string
}

// ============================================================================
// User Types
// ============================================================================

export interface User {
  id: string
  email: string
  name: string | null
  unit_system: UnitSystem
  created_at: string
  updated_at: string
}

export interface UserUpdateRequest {
  unit_system?: UnitSystem
  name?: string | null
}

// ============================================================================
// Equipment Types
// ============================================================================

export interface EquipmentBrief {
  id: string
  name: string
  description: string | null
}

export interface EquipmentListItem {
  id: string
  name: string
  description: string | null
  is_user_owned: boolean
}

export interface EquipmentOwnershipRequest {
  is_owned: boolean
}

export interface EquipmentOwnershipResponse {
  equipment_id: string
  is_owned: boolean
}

// ============================================================================
// Exercise Types
// ============================================================================

export interface ExerciseBrief {
  id: string
  name: string
  primary_muscle_groups: MuscleGroup[]
  secondary_muscle_groups: MuscleGroup[]
}

export interface ExerciseListItem {
  id: string
  name: string
  description: string | null
  primary_muscle_groups: MuscleGroup[]
  secondary_muscle_groups: MuscleGroup[]
  equipment: EquipmentBrief[]
  is_custom: boolean
}

export interface ExerciseListResponse {
  exercises: ExerciseListItem[]
  pagination: PaginationInfo
}

export interface PersonalRecordBrief {
  id: string
  record_type: RecordType
  value: number
  unit: string | null
  achieved_at: string
}

export interface ExerciseDetailResponse {
  id: string
  name: string
  description: string | null
  primary_muscle_groups: MuscleGroup[]
  secondary_muscle_groups: MuscleGroup[]
  default_weight: number | null
  default_reps: number | null
  default_rest_time_seconds: number | null
  equipment: EquipmentBrief[]
  personal_records: PersonalRecordBrief[]
  is_custom: boolean
  user_id: string | null
  created_at: string
  updated_at: string
}

export interface ExerciseSubstituteItem {
  id: string
  name: string
  description: string | null
  primary_muscle_groups: MuscleGroup[]
  secondary_muscle_groups: MuscleGroup[]
  equipment: EquipmentBrief[]
  match_score: number
}

export interface ExerciseCreateRequest {
  name: string
  primary_muscle_groups: MuscleGroup[]
  secondary_muscle_groups?: MuscleGroup[]
  description?: string | null
  default_weight?: number | null
  default_reps?: number | null
  default_rest_time_seconds?: number | null
  equipment_ids?: string[]
}

export interface ExerciseUpdateRequest {
  name?: string
  primary_muscle_groups?: MuscleGroup[]
  secondary_muscle_groups?: MuscleGroup[]
  description?: string | null
  default_weight?: number | null
  default_reps?: number | null
  default_rest_time_seconds?: number | null
  equipment_ids?: string[]
}

export interface ExerciseCreateResponse {
  id: string
  name: string
  is_custom: boolean
  created_at: string
}

// ============================================================================
// Workout Plan Types
// ============================================================================

export interface WorkoutPlanBrief {
  id: string
  name: string
}

export interface WorkoutExerciseDetail {
  id: string
  exercise: ExerciseBrief
  sequence: number
  sets: number
  reps_min: number
  reps_max: number
  rest_time_seconds: number | null
  confidence_level: ConfidenceLevel
}

// Workout (intermediate level between Plan and Exercises)
export interface WorkoutBrief {
  id: string
  name: string
  day_number: number | null
}

export interface WorkoutDetail {
  id: string
  name: string
  day_number: number | null
  order_index: number
  exercises: WorkoutExerciseDetail[]
  created_at: string
  updated_at: string
}

export interface WorkoutPlanListItem {
  id: string
  name: string
  description: string | null
  is_active: boolean
  workout_count: number
  exercise_count: number
  created_at: string
  updated_at: string
}

export interface WorkoutPlanListResponse {
  plans: WorkoutPlanListItem[]
  pagination: PaginationInfo
}

export interface WorkoutPlanDetailResponse {
  id: string
  name: string
  description: string | null
  is_active: boolean
  workouts: WorkoutDetail[]
  created_at: string
  updated_at: string
}

export interface WorkoutExerciseCreateItem {
  exercise_id: string
  sequence: number
  sets: number
  reps_min: number
  reps_max: number
  rest_time_seconds?: number | null
  confidence_level?: ConfidenceLevel
}

export interface WorkoutCreateItem {
  name: string
  day_number?: number | null
  order_index: number
  exercises: WorkoutExerciseCreateItem[]
}

export interface WorkoutPlanCreateRequest {
  name: string
  description?: string | null
  workouts: WorkoutCreateItem[]
}

export interface WorkoutPlanCreateResponse {
  id: string
  name: string
  created_at: string
}

export interface WorkoutPlanUpdateRequest {
  name?: string | null
  description?: string | null
  workouts?: WorkoutCreateItem[] | null
}

export interface WorkoutPlanUpdateResponse {
  id: string
  updated_at: string
}

export interface WorkoutPlanToggleActiveRequest {
  is_active: boolean
}

export interface WorkoutPlanToggleActiveResponse {
  id: string
  is_active: boolean
  updated_at: string
}

// ============================================================================
// Workout Session Types
// ============================================================================

export interface RecentSetInfo {
  reps: number
  weight: number
}

export interface RecentSessionInfo {
  date: string
  sets: RecentSetInfo[]
}

export interface ExerciseContextInfo {
  personal_record: PersonalRecordBrief | null
  recent_sessions: RecentSessionInfo[]
}

export interface PlannedExerciseWithContext {
  planned_exercise_id: string
  exercise: ExerciseBrief
  planned_sets: number
  planned_reps_min: number
  planned_reps_max: number
  rest_seconds: number | null
  context: ExerciseContextInfo
}

export interface WorkoutSessionStartRequest {
  workout_id: string
}

export interface WorkoutSessionStartResponse {
  session_id: string
  workout_plan: WorkoutPlanBrief
  workout: WorkoutBrief
  started_at: string
  exercises: PlannedExerciseWithContext[]
}

export interface ExerciseSetLogItem {
  set_number: number
  reps: number
  weight: number
  rest_time_seconds?: number | null
}

export interface LogExerciseRequest {
  exercise_id: string
  sets: ExerciseSetLogItem[]
}

export interface LogExerciseResponse {
  exercise_session_ids: string[]
}

export interface CompleteSessionRequest {
  notes?: string | null
}

export interface NewPersonalRecordInfo {
  exercise_name: string
  record_type: RecordType
  value: number
  unit: string | null
}

export interface CompleteSessionResponse {
  session_id: string
  status: SessionStatus
  duration_seconds: number
  new_personal_records: NewPersonalRecordInfo[]
}

export interface SkipSessionRequest {
  notes?: string | null
}

export interface SkipSessionResponse {
  session_id: string
  status: SessionStatus
}

export interface WorkoutSessionListItem {
  id: string
  workout_plan: WorkoutPlanBrief
  workout: WorkoutBrief
  status: SessionStatus
  started_at: string
  completed_at: string | null
  duration_seconds: number | null
  exercise_count: number
  notes: string | null
}

export interface WorkoutSessionListResponse {
  sessions: WorkoutSessionListItem[]
  pagination: PaginationInfo
}

export interface ExerciseSetDetail {
  id: string
  set_number: number
  reps_completed: number
  weight: number
  weight_unit: string
  is_warmup: boolean
  is_pr: boolean
  rpe: number | null
  notes: string | null
  completed_at: string
}

export interface ExerciseSessionDetail {
  id: string
  exercise: ExerciseBrief
  order_index: number
  notes: string | null
  sets: ExerciseSetDetail[]
}

// Backend returns flat structure - each entry is a single set
export interface ExerciseSessionFlatDetail {
  id: string
  exercise: ExerciseBrief
  set_number: number
  weight: number
  reps: number
  rest_time_seconds: number | null
  is_pr: boolean
  created_at: string
}

export interface PersonalRecordSummary {
  exercise_name: string
  value: number
  unit: string
}

export interface WorkoutSessionDetailResponse {
  id: string
  workout: WorkoutBrief
  workout_plan: WorkoutPlanBrief
  status: SessionStatus
  created_at: string
  updated_at: string
  notes: string | null
  exercise_sessions: ExerciseSessionFlatDetail[]
  personal_records: PersonalRecordSummary[]
}

// ============================================================================
// Personal Record Types
// ============================================================================

export interface PersonalRecordExerciseInfo {
  id: string
  name: string
}

export interface PersonalRecordListItem {
  id: string
  exercise: PersonalRecordExerciseInfo
  record_type: RecordType
  value: number
  unit: string | null
  achieved_at: string
  exercise_session_id: string | null
}

export interface PersonalRecordListResponse {
  records: PersonalRecordListItem[]
  pagination: PaginationInfo
}

export interface PersonalRecordCreateRequest {
  exercise_id: string
  record_type: RecordType
  value: number
  unit?: string | null
  achieved_at?: string | null
  notes?: string | null
}

export interface PersonalRecordCreateResponse {
  id: string
  record_type: RecordType
  value: number
}

// ============================================================================
// Stats Types
// ============================================================================

export interface MonthlyWorkoutCount {
  month: string // Format: YYYY-MM
  count: number
}

export interface MuscleGroupTrainingCount {
  muscle_group: MuscleGroup
  session_count: number
}

export interface StatsOverviewResponse {
  total_workouts: number
  total_duration_seconds: number
  total_volume_kg: number
  workouts_by_month: MonthlyWorkoutCount[]
  most_trained_muscle_groups: MuscleGroupTrainingCount[]
  current_streak_days: number
  personal_records_count: number
}

export interface ExerciseHistorySet {
  reps: number
  weight: number
  unit: string
}

export interface ExerciseHistorySession {
  date: string
  total_volume: number
  total_reps: number
  max_weight: number
  sets: ExerciseHistorySet[]
}

export interface ExerciseHistoryResponse {
  exercise: PersonalRecordExerciseInfo
  sessions: ExerciseHistorySession[]
}

// ============================================================================
// Stats Query Parameters
// ============================================================================

export interface StatsOverviewParams {
  start_date?: string
  end_date?: string
}

export interface ExerciseHistoryParams {
  start_date?: string
  end_date?: string
  limit?: number
}

// ============================================================================
// Common Query Parameters
// ============================================================================

export interface PaginationParams {
  page?: number
  limit?: number
}

export interface ExerciseListParams extends PaginationParams {
  muscle_group?: MuscleGroup
  equipment_id?: string
  search?: string
  user_equipment_only?: boolean
}

export interface WorkoutPlanListParams extends PaginationParams {
  search?: string
}

export interface WorkoutSessionListParams extends PaginationParams {
  status?: SessionStatus
}

export interface PersonalRecordListParams extends PaginationParams {
  exercise_id?: string
  record_type?: RecordType
}

// ============================================================================
// Plan Edit Types (Frontend-specific)
// ============================================================================

export interface EditableExercise {
  id: string // workout_exercise ID (or temp ID for new)
  exerciseId: string // actual exercise ID
  exerciseName: string
  primaryMuscleGroups: MuscleGroup[]
  secondaryMuscleGroups: MuscleGroup[]
  equipment: EquipmentBrief[]
  sequence: number
  sets: number
  repsMin: number
  repsMax: number
  restTimeSeconds: number | null
  confidenceLevel: ConfidenceLevel
  isNew: boolean // True if added during this edit session
  isModified: boolean // True if changed during this edit session
}

export interface PlanEditFormData {
  name: string
  description: string | null
  exercises: EditableExercise[]
}

export interface ExerciseFieldErrors {
  sets?: string
  repsMin?: string
  repsMax?: string
  restTimeSeconds?: string
}

export interface FormValidationErrors {
  name?: string
  description?: string
  exercises?: string // List-level error (e.g., "At least 1 exercise required")
  exerciseErrors: Map<string, ExerciseFieldErrors>
}

// ============================================================================
// Plan Import / Parse Types
// ============================================================================

export interface ParseWorkoutTextRequest {
  text: string
}

export interface ParsedExerciseMatch {
  exercise_id: string
  exercise_name: string
  original_text: string
  confidence: number
  confidence_level: ConfidenceLevel
  primary_muscle_groups: MuscleGroup[]
  secondary_muscle_groups: MuscleGroup[]
}

export interface ParsedExerciseItem {
  matched_exercise: ParsedExerciseMatch | null
  original_text: string
  sets: number
  reps_min: number
  reps_max: number
  rest_seconds: number | null
  notes: string | null
  sequence: number
  alternatives: ParsedExerciseMatch[]
}

export interface ParsedWorkoutItem {
  name: string
  day_number: number | null
  order_index: number
  exercises: ParsedExerciseItem[]
}

export interface ParsedWorkoutPlan {
  name: string
  description: string | null
  workouts: ParsedWorkoutItem[]
  raw_text: string
  import_log_id: string
}

export interface WorkoutPlanParseResponse {
  parsed_plan: ParsedWorkoutPlan
  total_exercises: number
  high_confidence_count: number
  medium_confidence_count: number
  low_confidence_count: number
  unmatched_count: number
}

export interface WorkoutPlanFromParsedRequest {
  import_log_id: string
  name: string
  description?: string | null
  workouts: WorkoutCreateItem[]
}

// ============================================================================
// Plan Import Wizard Types (Frontend-specific)
// ============================================================================

export type WizardStep = 1 | 2 | 3

export interface ImportWizardState {
  currentStep: WizardStep
  inputText: string
  isParsing: boolean
  parseError: string | null
  parsedData: ParsedWorkoutPlan | null
  parseStats: ParseStats | null
  isCreating: boolean
  createError: string | null
}

export interface ParseStats {
  total: number
  highConfidence: number
  mediumConfidence: number
  lowConfidence: number
  unmatched: number
}

export interface ParsedExerciseViewModel {
  id: string // Temp ID for UI tracking
  originalText: string
  matchedExercise: ParsedExerciseMatch | null
  alternativeMatches: ParsedExerciseMatch[]
  sets: number
  repsMin: number
  repsMax: number
  restSeconds: number | null
  notes: string | null
  confidenceLevel: ConfidenceLevel | null
  sequence: number
  isManuallyAdded: boolean
  isModified: boolean
}

export interface ParsedWorkoutViewModel {
  id: string // Temp ID for UI tracking
  name: string
  dayNumber: number | null
  orderIndex: number
  exercises: ParsedExerciseViewModel[]
}

export interface ImportedPlanFormData {
  name: string
  description: string | null
  workouts: ParsedWorkoutViewModel[]
  importLogId: string
}
