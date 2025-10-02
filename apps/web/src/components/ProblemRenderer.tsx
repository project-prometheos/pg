import { FormEvent, useState } from 'react';

import MathField from './math/MathField';
import type { ProblemResponse } from '../types';

type Props = {
  problem?: ProblemResponse;
  loading?: boolean;
  onSubmit: (values: Record<string, string>) => void;
};

const ProblemRenderer = ({ problem, loading = false, onSubmit }: Props) => {
  const [values, setValues] = useState<Record<string, string>>({});

  if (loading) {
    return <p>Loading problem…</p>;
  }

  if (!problem) {
    return <p>Select a problem to begin.</p>;
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit(values);
  };

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
      <p dangerouslySetInnerHTML={{ __html: problem.statementTex }} />
      {problem.inputs.map((input) => (
        <div key={input.name} className="flex flex-col gap-2">
          {input.label ? <label htmlFor={input.name}>{input.label}</label> : null}
          <MathField
            id={input.name}
            value={values[input.name] ?? ''}
            onChange={(next) => setValues((prev) => ({ ...prev, [input.name]: next }))}
          />
        </div>
      ))}
      <button type="submit" className="rounded bg-slate-900 px-4 py-2 font-semibold text-white">
        Submit answer
      </button>
    </form>
  );
};

export default ProblemRenderer;
