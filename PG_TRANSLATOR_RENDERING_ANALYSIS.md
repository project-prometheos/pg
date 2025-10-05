# PG Translator vs PG Renderer HTML Rendering Analysis

**Date**: 2025-01-XX
**Status**: ⚠️ Rendering differences identified

---

## Issue Summary

The user reports: **"currently the pg_translator doesn't seem to render the same HTML as the pg_renderer (markdown, better LaTeX)"**

---

## Architecture Comparison

### pg_renderer Architecture
```
PG Source → PGParser → PGEvaluator → PGMLRenderer → HTML
                           ↓                ↓
                      Variables      PGML → Markdown/KaTeX
```

**Key**: Single integrated PGML renderer that handles:
- ✅ Variable interpolation
- ✅ PGML math: `[`` ``]` → `$$...$$`, `[` `]` → `$...$`
- ✅ PGML formatting: `[*text*]` → `**text**`
- ✅ Answer blanks with placeholders
- ✅ Direct markdown output for frontend

### pg_translator Architecture
```
PG Source → Preprocessor → Executor → PGEnvironment → HTML
                ↓              ↓            ↓
          Transform PG    Run Python   Text Segments
                                            ↓
                                     PGMLParser → HTMLRenderer
                                                       ↓
                                                  LaTeX HTML
```

**Key**: Multi-stage with separate PGML rendering:
- TEXT blocks: Joined as raw strings (❌ **No rendering!**)
- PGML blocks: Parsed → HTMLRenderer → LaTeX notation (`\(...\)`, `\[...\]`)
- Backend: Converts LaTeX to Markdown (`$...$`, `$$...$$`)

---

## Current Flow in pg_translator

### 1. Preprocessor (`preprocessor.py`)

**TEXT blocks**:
```python
def _transform_text_block(self, content: str) -> str:
    # Transforms: $var → str(var)
    # Transforms: \{ans_rule(20)\} → ans_rule(20)
    # KEEPS LaTeX as-is: \( ... \) stays \( ... \)
    return ", ".join(segments)
```

Output: `TEXT("literal text with \\( x^2 \\) math", str(var), ans_rule(20))`

**PGML blocks**:
```python
# Store PGML content for runtime rendering
block_var = f"pgml_block_{len(text_blocks) - 1}"
escaped_content = self._escape_triple_quotes(block_content)
output_lines.append(f"{block_var} = '''\\n{escaped_content}\\n'''")
output_lines.append(f"TEXT(PGML({block_var}))")
```

### 2. Executor (`executor.py`)

```python
def render_text(self) -> str:
    # Plain TEXT segments - just joined!
    all_text = "\n".join(self.text_segments)  # ❌ NO RENDERING

    # PGML segments - parsed and rendered
    if self.pgml_segments:
        pgml_text = "\n\n".join(self.pgml_segments)
        doc = PGMLParser.parse_text(pgml_text)
        renderer = HTMLRenderer(context=self.variables)
        pgml_html = renderer.render(doc)

    return all_text + pgml_html
```

### 3. pg_pgml HTMLRenderer (`pg_pgml/renderer.py`)

```python
def visit_math_inline(self, node: MathInline) -> str:
    escaped_math = self._escape_html(node.content)
    return f'<span class="math-inline">\\({escaped_math}\\)</span>'
    # Output: \(...\) LaTeX notation

def visit_math_block(self, node: MathBlock) -> str:
    escaped_math = self._escape_html(node.content)
    return f'<div class="math-block">\\[{escaped_math}\\]</div>'
    # Output: \[...\] LaTeX notation
```

### 4. Backend Router (`database_problems.py`)

```python
def _pgml_to_markdown(pgml_text: str) -> str:
    # Convert \(...\) to $...$
    pgml_text = re.sub(r'\\\((.*?)\\\)', r'$\1$', pgml_text, flags=re.DOTALL)
    # Convert \[...\] to $$...$$
    pgml_text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', pgml_text, flags=re.DOTALL)
    return pgml_text

# Applied to output:
statement_html = _pgml_to_markdown(rendered['statement_html'])
```

### 5. Frontend (`Markdown.tsx`)

```tsx
<ReactMarkdown
    remarkPlugins={[remarkMath, remarkGfm]}
    rehypePlugins={[rehypeRaw, rehypeKatex]}
>
    {children}  {/* Expects $...$ and $$...$$ */}
</ReactMarkdown>
```

---

## Problem Analysis

### Issue 1: TEXT Blocks Not Rendered ❌

**TEXT blocks are concatenated without any HTML rendering:**

```python
# executor.py line 120
all_text = "\n".join(self.text_segments)  # Just raw strings!
```

**Example**:
- Input TEXT: `The answer is $a and the formula is \( x^2 + 1 \).`
- After preprocessor: `TEXT("The answer is ", str(a), " and the formula is \\( x^2 + 1 \\).")`
- After execution: Raw text segments joined
- Output: `"The answer is 3 and the formula is \( x^2 + 1 \)."`
- Problem: LaTeX `\(...\)` not converted to markdown `$...$`

### Issue 2: PGML Rendering Works ✅

**PGML blocks ARE properly rendered:**

```python
# PGML input: [` x^2 `]
# PGMLParser → MathInline node
# HTMLRenderer → <span class="math-inline">\(x^2\)</span>
# _pgml_to_markdown() → <span class="math-inline">$x^2$</span>
# Frontend → Renders with KaTeX ✅
```

---

## Comparison with pg_renderer

### pg_renderer Approach

**Everything goes through PGMLRenderer:**

```python
# pg_renderer/pgml.py
class PGMLRenderer:
    def render(self, pgml: str) -> Tuple[str, Dict[str, str]]:
        # 1. Variable interpolation FIRST
        html = re.sub(r'\[\$(\w+)\]', self._interpolate_var, html)

        # 2. Display math: [`` ... ``] → $$...$$
        html = re.sub(r'\[``(.*?)``\]', r'$$\1$$', html, flags=re.DOTALL)

        # 3. Inline math: [` ... `] → $...$
        html = re.sub(r'\[`(.*?)`\]', r'$\1$', html)

        # 4. Answer blanks: [_____]{$answer} → ___ANSWER_BLANK_AnSwEr0001___
        html = re.sub(r'\[_+\]\{([^}]+)\}(?:\{[0-9]+\})?', self._create_answer_blank, html)

        # 5. Formatting: [*text*] → **text**, [|text|] → *text*
        html = re.sub(r'\[\*(.*?)\*\]', r'**\1**', html)
        html = re.sub(r'\[\|(.*?)\|\]', r'*\1*', html)

        return html, self.answer_blanks
```

**Result**: Direct markdown output ready for frontend

---

## Root Cause

**TEXT blocks in pg_translator bypass PGML rendering entirely:**

1. Preprocessor transforms TEXT blocks into Python `TEXT()` calls
2. These are executed and stored as plain strings in `env.text_segments`
3. `render_text()` just joins them with `"\n".join()`
4. No PGML-to-markdown conversion happens for TEXT content

**PGML blocks work correctly** because they go through the full PGML pipeline.

---

## Solutions

### Option A: Post-process TEXT Segments (Quick Fix) ⚡

Apply PGML-to-markdown conversion to ALL text segments in `executor.py`:

```python
def render_text(self) -> str:
    # Combine plain text - but APPLY PGML transformation
    text_html = self._pgml_to_markdown("\n".join(self.text_segments))

    # Render PGML segments
    pgml_html = ""
    if self.pgml_segments:
        pgml_text = "\n\n".join(self.pgml_segments)
        doc = PGMLParser.parse_text(pgml_text)
        renderer = HTMLRenderer(context=self.variables)
        pgml_html = renderer.render(doc)
        pgml_html = self._pgml_to_markdown(pgml_html)

    # Combine
    if text_html and pgml_html:
        return text_html + "\n" + pgml_html
    return text_html + pgml_html

def _pgml_to_markdown(self, text: str) -> str:
    """Convert PGML/LaTeX notation to markdown."""
    # Inline math: \(...\) → $...$
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    # Display math: \[...\] → $$...$$
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    return text
```

### Option B: Render TEXT as PGML (Better Architecture) 🏗️

Treat TEXT blocks as PGML and parse them properly:

```python
def render_text(self) -> str:
    # Combine ALL text (TEXT + PGML) and parse as PGML
    all_pgml = "\n\n".join(self.text_segments + self.pgml_segments)

    if not all_pgml:
        return ""

    doc = PGMLParser.parse_text(all_pgml)
    renderer = HTMLRenderer(context=self.variables)
    html = renderer.render(doc)

    # Convert LaTeX to markdown
    html = self._pgml_to_markdown(html)
    return html
```

### Option C: Backend-Only Fix (Current Approach) ✅

Keep current architecture but ensure `_pgml_to_markdown()` is comprehensive:

```python
def _pgml_to_markdown(pgml_text: str) -> str:
    if not pgml_text:
        return pgml_text

    # Inline math: \(...\) → $...$
    pgml_text = re.sub(r'\\\((.*?)\\\)', r'$\1$', pgml_text, flags=re.DOTALL)

    # Display math: \[...\] → $$...$$
    pgml_text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', pgml_text, flags=re.DOTALL)

    # Bold: <strong> → **
    pgml_text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', pgml_text)

    # Italic: <em> → *
    pgml_text = re.sub(r'<em>(.*?)</em>', r'*\1*', pgml_text)

    return pgml_text
```

---

## Recommendation

**Use Option A (Post-process TEXT Segments) immediately** because:

1. ✅ Minimal code change (add one method to `executor.py`)
2. ✅ Fixes LaTeX rendering in TEXT blocks
3. ✅ Preserves existing PGML pipeline
4. ✅ Backend router already does this - extend to executor

Then consider **Option B for long-term** to unify TEXT and PGML handling.

---

## Implementation

### Step 1: Add method to `PGEnvironment` in `executor.py`

```python
def _pgml_to_markdown(self, text: str) -> str:
    """Convert PGML/LaTeX notation to markdown for frontend."""
    if not text:
        return text

    import re

    # Inline math: \(...\) → $...$
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)

    # Display math: \[...\] → $$...$$
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)

    return text
```

### Step 2: Apply in `render_text()`

```python
def render_text(self) -> str:
    """Render all text segments to HTML."""
    # Convert TEXT segments
    text_html = self._pgml_to_markdown("\n".join(self.text_segments))

    # Render PGML segments
    pgml_html = ""
    if self.pgml_segments:
        pgml_text = "\n\n".join(self.pgml_segments)
        doc = PGMLParser.parse_text(pgml_text)
        renderer = HTMLRenderer(context=self.variables)
        pgml_html = self._pgml_to_markdown(renderer.render(doc))

    # Combine
    if text_html and pgml_html:
        return text_html + "\n" + pgml_html
    return text_html + pgml_html
```

### Step 3: Apply to solution and hint

```python
def render_solution(self) -> str | None:
    """Render solution text to HTML."""
    if not self.solution_segments:
        return None
    return self._pgml_to_markdown("\n".join(self.solution_segments))

def render_hint(self) -> str | None:
    """Render hint text to HTML."""
    if not self.hint_segments:
        return None
    return self._pgml_to_markdown("\n".join(self.hint_segments))
```

---

## Testing Plan

1. Test TEXT block with LaTeX: `\( x^2 \)` → should render as math
2. Test PGML block with math: `[` x^2 `]` → should still work
3. Test mixed TEXT + PGML
4. Test solution/hint blocks
5. Verify no regressions in existing problems

---

## Status: Ready to Implement ✅

This fix will bring pg_translator rendering to parity with pg_renderer!
