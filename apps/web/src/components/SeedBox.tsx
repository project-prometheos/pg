import { ChangeEvent, useState } from 'react';

type Props = {
  seed: number;
  loading?: boolean;
  onChange: (seed: number) => void;
};

const SeedBox = ({ seed, loading = false, onChange }: Props) => {
  const [value, setValue] = useState(seed);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const next = Number(event.target.value);
    setValue(next);
  };

  const handleBlur = () => {
    onChange(value);
  };

  const randomize = () => {
    const next = Math.floor(Math.random() * 10_000);
    setValue(next);
    onChange(next);
  };

  return (
    <div className="flex items-center gap-4">
      <label className="flex items-center gap-2">
        <span>Seed</span>
        <input
          className="w-24 rounded border border-slate-300 px-2 py-1"
          type="number"
          value={value}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={loading}
        />
      </label>
      <button
        type="button"
        className="rounded border border-slate-200 px-3 py-1"
        onClick={randomize}
        disabled={loading}
      >
        Randomize
      </button>
    </div>
  );
};

export default SeedBox;
