import { useParams } from 'react-router-dom';

import { useQuery } from '@tanstack/react-query';

import Markdown from '../components/Markdown';
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
			<Markdown className="mt-4 rounded bg-slate-100 p-4">{data?.solutionTex ?? ''}</Markdown>
		</article>
	);
};

export default SolutionPage;
