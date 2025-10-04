import 'katex/dist/katex.min.css';

import ReactMarkdown from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';

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
			{/* rehypeRaw must run before rehypeKatex so math nodes are available for KaTeX rendering */}
			<ReactMarkdown remarkPlugins={[remarkMath, remarkGfm]} rehypePlugins={[rehypeRaw, rehypeKatex]}>
				{children}
			</ReactMarkdown>
		</div>
	);
};

export default Markdown;
