import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';

import { fetchSolution } from '../services/api';

const SolutionPage = () => {
  const { variantId } = useParams();
  const { data, isPending } = useQuery({
    queryKey: ['solution', variantId],
    queryFn: () => fetchSolution(variantId ?? ''),
    enabled: Boolean(variantId),
  });

  if (!variantId) {
    return <p className="p-6">Missing variant identifier.</p>;
  }

  if (isPending) {
    return <p className="p-6">Loading solution…</p>;
  }

  return (
    <article className="mx-auto max-w-3xl p-6">
      <h1 className="text-2xl font-semibold">Solution</h1>
      <pre className="mt-4 whitespace-pre-wrap rounded bg-slate-100 p-4">{data?.solutionTex}</pre>
    </article>
  );
};

export default SolutionPage;
