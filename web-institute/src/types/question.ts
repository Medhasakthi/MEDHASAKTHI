/**
 * Question and AI generation types
 */

export enum QuestionType {
  MULTIPLE_CHOICE = 'multiple_choice',
  TRUE_FALSE = 'true_false',
  FILL_IN_BLANK = 'fill_in_blank',
  SHORT_ANSWER = 'short_answer',
  ESSAY = 'essay',
  CODE = 'code',
  IMAGE_BASED = 'image_based',
  AUDIO_BASED = 'audio_based',
}

export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
}

export enum QuestionStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ARCHIVED = 'archived',
}

export interface QuestionOption {
  id: string;
  text: string;
  is_correct: boolean;
}

export interface Question {
  id: string;
  question_text: string;
  question_type: QuestionType;
  difficulty_level: DifficultyLevel;
  subject_id: string;
  topic_id?: string;
  grade_level?: string;
  
  options?: QuestionOption[];
  correct_answer?: string;
  explanation?: string;
  hints?: string[];
  
  image_url?: string;
  audio_url?: string;
  video_url?: string;
  
  ai_generated: boolean;
  ai_model_used?: string;
  
  quality_score: number;
  difficulty_score: number;
  times_used: number;
  times_correct: number;
  
  status: QuestionStatus;
  created_at: string;
  updated_at?: string;
  
  tags?: string[];
  keywords?: string[];
}

export interface Subject {
  id: string;
  name: string;
  code: string;
  description?: string;
  parent_subject_id?: string;
  level: number;
  is_active: boolean;
  created_at: string;
}

export interface Topic {
  id: string;
  subject_id: string;
  name: string;
  description?: string;
  learning_objectives?: string[];
  prerequisites?: string[];
  is_active: boolean;
  created_at: string;
}

export interface QuestionGenerationRequest {
  subject_id: string;
  topic_id?: string;
  question_type: QuestionType;
  difficulty_level: DifficultyLevel;
  count: number;
  grade_level?: string;
  learning_objective?: string;
  context?: string;
}

export interface QuestionGenerationResponse {
  success: boolean;
  message: string;
  generation_id?: string;
  questions_generated: number;
  questions: Question[];
  generation_time: number;
  cost?: number;
}

export interface QuestionBank {
  id: string;
  name: string;
  description?: string;
  institute_id?: string;
  is_public: boolean;
  is_ai_generated: boolean;
  auto_update: boolean;
  total_questions: number;
  subjects_covered?: string[];
  difficulty_distribution?: Record<string, number>;
  created_at: string;
  updated_at?: string;
}

export interface QuestionSearchParams {
  query?: string;
  subject_id?: string;
  topic_id?: string;
  question_type?: QuestionType;
  difficulty_level?: DifficultyLevel;
  grade_level?: string;
  tags?: string[];
  ai_generated?: boolean;
  status?: QuestionStatus;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface QuestionSearchResponse {
  questions: Question[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface AIGenerationStats {
  total_generations: number;
  total_questions_generated: number;
  total_questions_approved: number;
  average_generation_time: number;
  total_cost: number;
  success_rate: number;
  by_question_type: Record<string, number>;
  by_difficulty: Record<string, number>;
  by_subject: Record<string, number>;
  recent_generations: Array<{
    id: string;
    created_at: string;
    question_type: string;
    difficulty_level: string;
    count_generated: number;
    status: string;
  }>;
}

export interface QuestionFeedback {
  question_id: string;
  feedback_type: string;
  rating?: number;
  comment?: string;
  is_unclear?: boolean;
  is_incorrect?: boolean;
  is_too_easy?: boolean;
  is_too_hard?: boolean;
  has_typos?: boolean;
}

export interface QuestionValidation {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
  quality_score: number;
}
