// Search API service for frontend
import type { ProblemSummary, SearchResponse, FacetResponse } from '../types';

const BASE_URL = '/api';

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

export const searchProblems = async (filters: SearchFilters): Promise<SearchResponse[]> => {
  const params = new URLSearchParams();
  
  if (filters.query) params.append('q', filters.query);
  if (filters.types) params.append('types', filters.types.join(','));
  if (filters.subjects) params.append('subjects', filters.subjects.join(','));
  if (filters.categories) params.append('categories', filters.categories.join(','));
  if (filters.keywords) params.append('keywords', filters.keywords.join(','));
  if (filters.macros) params.append('macros', filters.macros.join(','));
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.offset) params.append('offset', filters.offset.toString());

  const response = await fetch(`${BASE_URL}/search?${params}`);
  if (!response.ok) {
    throw new Error('Search failed');
  }
  return response.json();
};

export const fullTextSearch = async (query: string, limit: number = 50): Promise<SearchResponse[]> => {
  const params = new URLSearchParams();
  params.append('q', query);
  params.append('limit', limit.toString());

  const response = await fetch(`${BASE_URL}/fts?${params}`);
  if (!response.ok) {
    throw new Error('Full-text search failed');
  }
  return response.json();
};

export const getProblemsByCategory = async (category: string, limit: number = 50): Promise<ProblemSummary[]> => {
  const response = await fetch(`${BASE_URL}/by-category/${encodeURIComponent(category)}?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to get problems by category');
  }
  return response.json();
};

export const getProblemsBySubject = async (subject: string, limit: number = 50): Promise<ProblemSummary[]> => {
  const response = await fetch(`${BASE_URL}/by-subject/${encodeURIComponent(subject)}?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to get problems by subject');
  }
  return response.json();
};

export const getProblemsByMacro = async (macro: string, limit: number = 50): Promise<ProblemSummary[]> => {
  const response = await fetch(`${BASE_URL}/by-macro/${encodeURIComponent(macro)}?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to get problems by macro');
  }
  return response.json();
};

export const getRelatedProblems = async (problemId: string, limit: number = 10): Promise<ProblemSummary[]> => {
  const response = await fetch(`${BASE_URL}/related/${encodeURIComponent(problemId)}?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to get related problems');
  }
  return response.json();
};

export const getSearchFacets = async (): Promise<FacetResponse> => {
  const response = await fetch(`${BASE_URL}/facets`);
  if (!response.ok) {
    throw new Error('Failed to get search facets');
  }
  return response.json();
};

export const getProblemDetails = async (problemId: string): Promise<ProblemSummary> => {
  const response = await fetch(`${BASE_URL}/problem/${encodeURIComponent(problemId)}`);
  if (!response.ok) {
    throw new Error('Failed to get problem details');
  }
  return response.json();
};
