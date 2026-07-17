export interface User {
  id: string;
  username: string;
  real_name?: string;
  role: 'super_admin' | 'admin' | 'teacher' | 'student';
  email?: string;
  phone?: string;
  is_active: boolean;
  created_at?: string;
}

export interface Marker {
  point_index: number;
  x: number;
  y: number;
  label?: string;
}

export interface Zone {
  id?: string;
  zone_type: 'student_info' | 'objective' | 'subjective';
  label?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  sort_order?: number;
}

export interface Question {
  id?: string;
  question_number: number;
  question_type: 'single' | 'multiple' | 'judge';
  options_count: number;
  options?: string[];
  option_layout: 'horizontal' | 'vertical';
  score: number;
  correct_answer?: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  sort_order?: number;
}

export interface Template {
  id: string;
  name: string;
  description?: string;
  subject?: string;
  grade?: string;
  exam_name?: string;
  image_path: string;
  image_width?: number;
  image_height?: number;
  total_score: number;
  objective_score: number;
  subjective_score: number;
  info_method: 'omr' | 'barcode';
  status: string;
  created_by?: string;
  created_at?: string;
  markers: Marker[];
  zones: Zone[];
  questions: Question[];
}

export interface ScanBatch {
  id: string;
  name: string;
  template_id: string;
  exam_name?: string;
  total: number;
  processed: number;
  failed: number;
  status: string;
  created_at?: string;
}

export interface ScannedSheet {
  id: string;
  filename: string;
  student_id?: string;
  student_name?: string;
  status: string;
  error_message?: string;
}

export interface GradingTask {
  id: string;
  name: string;
  batch_id: string;
  template_id: string;
  status: string;
  total_subjective: number;
  graded_count: number;
  threshold: number;
  created_at?: string;
  assignments: GradingAssignment[];
}

export interface GradingAssignment {
  id: string;
  teacher_id: string;
  question_number: number;
  total_count: number;
  graded_count: number;
  status: string;
}

export interface ExamScore {
  id: string;
  student_id?: string;
  student_name?: string;
  objective_score: number;
  subjective_score: number;
  total_score: number;
  full_score?: number;
  rank?: string;
}
