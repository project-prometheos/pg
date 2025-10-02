import type { CheckResponse, ProblemResponse } from '../types';

const BASE_URL = '/api';

export const fetchProblem = async (id: string, seed: number): Promise<ProblemResponse> => {
  const response = await fetch(`${BASE_URL}/problems/${id}?seed=${seed}`);
  if (!response.ok) {
    throw new Error('Failed to load problem');
  }
  const json = await response.json();
  return {
    variantId: json.variant_id,
    problemId: json.problem_id,
    seed: json.seed,
    statementTex: json.statement_tex,
    inputs: json.inputs,
    solutionTex: json.solution_tex,
    meta: json.meta,
  } satisfies ProblemResponse;
};

export const submitAttempt = async ({
  variantId,
  inputs,
}: {
  variantId: string;
  inputs: Record<string, string>;
}): Promise<CheckResponse> => {
  const response = await fetch(`${BASE_URL}/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ variant_id: variantId, inputs }),
  });
  if (!response.ok) {
    throw new Error('Submission failed');
  }
  return response.json();
};

export const fetchSolution = async (variantId: string): Promise<{ solutionTex: string }> => {
  const response = await fetch(`${BASE_URL}/solution/${variantId}`);
  if (!response.ok) {
    throw new Error('Solution not found');
  }
  return response.json();
};
