import type { CheckResponse } from '../types';

type Props = {
  feedback: CheckResponse | null;
};

const Feedback = ({ feedback }: Props) => {
  if (!feedback) return null;

  return (
    <aside className="rounded border border-slate-200 bg-slate-50 p-4">
      <p className="font-semibold">Result</p>
      <p>{feedback.correct ? 'Correct!' : 'Try again.'}</p>
      {feedback.feedback?.length ? (
        <ul className="mt-2 list-disc pl-4">
          {feedback.feedback.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      ) : null}
    </aside>
  );
};

export default Feedback;
