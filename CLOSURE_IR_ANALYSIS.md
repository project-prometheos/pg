# Closure IR Structure Analysis

## 1. THE EXACT IR STRUCTURE (from grammar lines 1296-1299 and transformer lines 1470-1478)

IR Tuple Format:
```
("if", condition_ir, block_ir, [clause_list])
```

Where:
- Element 0: "if" string 
- Element 1: condition_ir (expression IR tuple)
- Element 2: block_ir tuple: ("block", [statement_list])
- Element 3: [clause_list] containing:
  - ("elsif", condition_ir, block_ir)
  - ("else", block_ir)

Example from AlgebraicFractionAnswer.pg (lines 69-98):
- 3 param_unpack statements (parameter assignments)
- 1 if statement with condition and block
- 5 elsif clauses, each with condition and block  
- 1 else clause with block
- Some branches contain side effects (method calls to self.setMessage)

## 2. WHAT THE CURRENT _emit_closure TRIES TO DO (lines 1994-2066)

Current approach:
1. Extract params from param_unpack statements
2. If single return: emit as lambda
3. If complex: emit as IIFE with nested def

The broken code (lines 2046-2064):
```python
lines.append(f"(lambda: (")
lines.append(f"{'    ' * (indent + 1)}def {func_name}({params_str}):")
# ... emit statements ...
lines.append(f"{'    ' * (indent + 1)}return {func_name}")
lines.append(f"{'    ' * indent}))()")
```

This produces INVALID PYTHON SYNTAX because:
- def is a statement, not an expression
- You cannot nest def inside parentheses or lambda body
- Python has no IIFE pattern like JavaScript

## 3. WHY IT FAILS FOR AlgebraicFractionAnswer.pg

The checker closure fails because:
1. Has multiple param_unpack statements PLUS an if/elsif/else block
2. Falls through to "complex closure" case
3. Tries to emit as IIFE with nested def
4. Produces invalid Python syntax

## 4. THE SIMPLEST CORRECT APPROACH

For complex closures (control flow + multiple statements):

EMIT AS A DEF FUNCTION, NOT A LAMBDA

Input Perl:
```perl
checker => sub {
    my ($correct, $student, $self) = @_;
    my ($f1stu, $f2stu) = @$student;
    if (condition1) {
        return [1, 1];
    } elsif (condition2) {
        return [1, 0];
    } else {
        return [0, 0];
    }
}
```

Output Python:
```python
def _closure_checker_abc123(correct, student, self):
    f1stu, f2stu = student
    if condition1:
        return [1, 1]
    elif condition2:
        return [1, 0]
    else:
        return [0, 0]

checker=_closure_checker_abc123
```

## 5. WHY THIS WORKS

1. Valid Python syntax - def is a statement
2. Control flow works - if/elif/else are statements (not ternary)
3. Side effects work - method calls execute normally
4. Captures parameters - function signature matches
5. Multiple returns - each branch can return different value
6. Readable - matches Perl code structure

## 6. DETECTING COMPLEXITY IN _emit_closure

Check if closure body (after param_unpack) contains:
- if/unless statements
- while/for/foreach loops
- do-until loops
- Multiple statements (not just single return)
- Statements with side effects

If ANY of these: MUST emit as def function, NOT lambda

## 7. WHETHER TO USE EXPRESSIONS VS STATEMENTS

For closures with control flow: MUST use statements (def), NOT expressions (lambda)

Why NOT ternary operators:
- Only work for single-value returns
- Unreadable with 5+ branches (AlgebraicFractionAnswer has 5+ elif)
- Cannot handle side effects or multiple statements per branch
- AlgebraicFractionAnswer has method calls: self.setMessage()

## 8. IMPLEMENTATION SUMMARY

Current code:
- IR structure is CORRECT (lines 1470-1478 create proper tuples)
- _emit_ir method is CORRECT (lines 1850-1870 emit proper if/elif/else)
- _emit_closure is BROKEN (lines 1994-2066 try invalid IIFE pattern)

Solution:
1. Detect complexity in closure body
2. For simple (single return): lambda
3. For complex: def with unique generated name
4. Return function name as the value

The EXACT fix:
- Replace the IIFE pattern with proper def emission
- Generate unique function names (e.g., _closure_func_{id:x})
- Emit as multi-line def statement
- Return just the function name
