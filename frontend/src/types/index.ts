// Types for Math Mentor AI Frontend

// Parser Types
export interface ParsedProblem {
  problem_text: string;
  topic: string;
  variables: string[];
  constraints: string[];
  needs_clarification: boolean;
  clarification_reason: string;
}

// Solver Types
export interface ToolCall {
  tool: string;
  input: string;
  output: string;
}

export interface SolverResult {
  solution: string;
  final_answer: string;
  tool_calls: ToolCall[];
}

// Verifier Types
export interface VerifierResult {
  is_correct: boolean;
  confidence: number;
  issues: string[];
  corrected_answer: string;
  reasoning: string;
  needs_hitl: boolean;
}

// Explainer Types
export interface ExplanationResult {
  explanation: string;
  final_answer: string;
  confidence: number;
}

// RAG Types
export interface RetrievedSource {
  title: string;
  source: string;
  section: string;
  snippet: string;
  score: number;
}

// Memory Types
export interface MemoryRecord {
  id: string;
  raw_input: string;
  parsed_problem: ParsedProblem;
  solver_result: SolverResult;
  verifier_result: VerifierResult;
  explanation: ExplanationResult;
  user_feedback?: string;
  user_comment?: string;
  timestamp: string;
}

export interface MemorySummary {
  id: string;
  problem_text: string;
  topic: string;
  final_answer: string;
  user_feedback?: string;
  timestamp: string;
}

// API Request/Response Types
export interface SolveRequest {
  input_type: 'text' | 'image' | 'audio';
  content: string;
  filename?: string;
}

export interface SolveResponse {
  parsed_problem: ParsedProblem;
  solver_result: SolverResult;
  verifier_result: VerifierResult;
  explanation: ExplanationResult;
  retrieved_sources: RetrievedSource[];
  hitl_required: boolean;
  memory_id: string;
}

export interface ExtractionResponse {
  extracted_text: string;
  confidence: 'high' | 'medium' | 'low';
  needs_review: boolean;
  notes: string;
}

export interface TranscriptionResponse {
  transcript: string;
  cleaned_text: string;
  language: string;
  duration_seconds: number;
  needs_review: boolean;
  notes: string;
}

export interface HITLResponse {
  approved: boolean;
  edited_answer?: string;
  comment?: string;
}

export interface FeedbackRequest {
  feedback: 'correct' | 'incorrect';
  comment?: string;
}

// Chat Types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    extractedText?: string;
    confidence?: string;
    needsReview?: boolean;
    imageUrl?: string;
    audioUrl?: string;
  };
}

// App State Types
export type InputMode = 'text' | 'image' | 'audio';

export type InspectorTab = 'history' | 'trace' | 'context';

export interface AgentStep {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  icon: string;
}
