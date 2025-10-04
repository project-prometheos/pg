# Markdown Component

A comprehensive markdown renderer for the web app with full LaTeX math support.

## Features

- **LaTeX Math Rendering**
  - Inline math: `$x^2 + y^2 = z^2$`
  - Display math: `$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$`
  - Powered by KaTeX for fast, high-quality rendering

- **GitHub Flavored Markdown (GFM)**
  - Tables
  - Strikethrough (`~~text~~`)
  - Task lists (`- [ ]` and `- [x]`)
  - Autolink literals

- **Raw HTML Support**
  - Embed HTML elements when needed
  - Useful for complex layouts

## Usage

```tsx
import Markdown from './components/Markdown';

<Markdown className="prose">
  # Hello World

  This is some **bold** and *italic* text.

  Inline math: $E = mc^2$

  Display math:
  $$
  \frac{d}{dx} \sin(x) = \cos(x)
  $$

  | Column 1 | Column 2 |
  |----------|----------|
  | Data 1   | Data 2   |
</Markdown>
```

## Implementation

The component uses:
- `react-markdown` - Core markdown parsing and rendering
- `remark-math` - Math syntax support
- `remark-gfm` - GitHub Flavored Markdown extensions
- `rehype-katex` - KaTeX rendering for math
- `rehype-raw` - Raw HTML support

## Current Usage

The Markdown component is used in:
- **ProblemRenderer** - Renders problem statements with math
- **SolutionPage** - Displays solutions with formatting
- **Feedback** - Shows feedback messages with potential math/formatting

## Math Syntax Examples

### Inline Math
```markdown
The quadratic formula is $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$.
```

### Display Math
```markdown
$$
\begin{aligned}
  f(x) &= x^2 + 2x + 1 \\
  &= (x+1)^2
\end{aligned}
$$
```

### Common Symbols
- Greek letters: `$\alpha, \beta, \gamma, \Delta, \Omega$`
- Operators: `$\sum, \prod, \int, \lim$`
- Relations: `$\leq, \geq, \approx, \equiv, \neq$`
- Arrows: `$\rightarrow, \Rightarrow, \leftrightarrow$`

## Styling

The component accepts a `className` prop for styling. Consider using Tailwind's typography plugin for better default styles:

```tsx
<Markdown className="prose prose-slate max-w-none">
  {content}
</Markdown>
```
