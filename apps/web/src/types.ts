export type InputSpec = {
  name: string;
  type: string;
  label?: string | null;
};

export type ProblemResponse = {
  variantId: string;
  problemId: string;
  seed: number;
  statementTex: string;
  inputs: InputSpec[];
  solutionTex: string;
  meta: Record<string, string>;
};

export type CheckResponse = {
  correct: boolean;
  score: number;
  feedback?: string[];
  canonical?: string;
};
