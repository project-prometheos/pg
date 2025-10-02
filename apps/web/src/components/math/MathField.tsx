import { useEffect, useRef } from 'react';
import type { DetailedHTMLProps, HTMLAttributes } from 'react';
import 'mathlive';
import type { MathfieldElement } from 'mathlive';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'math-field': DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement>;
    }
  }
}

export type MathFieldProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
};

const MathField = ({ id, value, onChange }: MathFieldProps) => {
  const ref = useRef<MathfieldElement | null>(null);

  useEffect(() => {
    if (!ref.current) {
      const element = document.getElementById(id) as MathfieldElement | null;
      if (element) {
        ref.current = element;
        element.addEventListener('input', () => onChange(element.getValue('latex')));
      }
    } else if (ref.current.getValue('latex') !== value) {
      ref.current.setValue(value, { silenceNotifications: true });
    }
  }, [id, onChange, value]);

  return <math-field id={id} defaultValue={value}></math-field>;
};

export default MathField;
