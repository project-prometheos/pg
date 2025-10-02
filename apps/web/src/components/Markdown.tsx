import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import 'katex/dist/katex.min.css';

type MarkdownProps = {
  children: string;
  className?: string;
};

/**
 * Markdown renderer with support for:
 * - LaTeX math (inline with $...$ and display with $$...$$)
 * - GitHub Flavored Markdown (tables, strikethrough, task lists, etc.)
 * - Raw HTML
 * - KaTeX for math rendering
 */
const Markdown = ({ children, className }: MarkdownProps) => {
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkMath, remarkGfm]}
        rehypePlugins={[rehypeKatex, rehypeRaw]}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
};

export default Markdown;
