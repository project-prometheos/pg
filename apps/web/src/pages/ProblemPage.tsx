import { useMemo } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { fetchProblem, submitAttempt } from '../services/api';
import Feedback from '../components/Feedback';
import ProblemRenderer from '../components/ProblemRenderer';
import SeedBox from '../components/SeedBox';

const DEFAULT_PROBLEM = 'calc.product_rule.v1';

const ProblemPage = () => {
  const params = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const problemId = params.id ?? DEFAULT_PROBLEM;
  const seed = Number(searchParams.get('seed') ?? '0');

  const { data, isPending } = useQuery({
    queryKey: ['problem', problemId, seed],
    queryFn: () => fetchProblem(problemId, seed),
  });

  const mutation = useMutation({
    mutationFn: submitAttempt,
  });

  const onSeedChange = (nextSeed: number) => {
    setSearchParams({ seed: String(nextSeed) });
    navigate(`/p/${problemId}?seed=${nextSeed}`);
  };

  const onSubmit = (values: Record<string, string>) => {
    if (!data) return;
    mutation.mutate({
      variantId: data.variantId,
      inputs: values,
    });
  };

  const feedback = useMemo(() => mutation.data ?? null, [mutation.data]);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 p-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">Problem: {problemId}</h1>
        <SeedBox seed={seed} onChange={onSeedChange} loading={isPending} />
      </header>
      <main>
        <ProblemRenderer problem={data} loading={isPending} onSubmit={onSubmit} />
      </main>
      <Feedback feedback={feedback} />
    </div>
  );
};

export default ProblemPage;
