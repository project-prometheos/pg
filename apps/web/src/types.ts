// Updated types for search functionality
export interface ProblemSummary {
  id: string;
  name: string;
  description?: string;
  file_path?: string;
  types: string[];
  subjects: string[];
  categories: string[];
  keywords: string[];
  macros: string[];
  created_at: string;
  updated_at: string;
}

export interface SearchResponse {
  results: ProblemSummary[];
  total: number;
  query?: string;
  filters: Record<string, any>;
  score?: number;
  matched_fields?: string[];
}

export interface FacetResponse {
  categories: string[];
  subjects: string[];
  types: string[];
  macros: string[];
}

export interface SearchFilters {
  query?: string;
  types?: string[];
  subjects?: string[];
  categories?: string[];
  keywords?: string[];
  macros?: string[];
  limit?: number;
  offset?: number;
}

// Existing types
export interface ProblemResponse {
  variantId: string;
  problemId: string;
  seed: number;
  statementTex: string;
  inputs: InputSpec[];
  solutionTex: string;
  meta: Record<string, any>;
}

export interface InputSpec {
  name: string;
  type: string;
  label?: string;
  meta?: Record<string, any>;
}

export interface CheckResponse {
  correct: boolean;
  feedback?: string;
  score?: number;
}