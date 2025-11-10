import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))

from pg_translator.pg_preprocessor_pygment import PGPreprocessor

# Test ParametricPlot line 72 - two method chains with division
source_lines = [
    "$m = $y->D('t')->eval(t => 'pi/3') / $x->D('t')->eval(t => 'pi/3');",
]

source = "\n".join(source_lines)
print("Input source:")
for i, line in enumerate(source_lines, 1):
    print(f"{i:2d}: {line}")

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(source)

print("\n\nOutput lines:")
out_lines = result.code.split('\n')
for i, line in enumerate(out_lines, 1):
    if line.strip():
        print(f"{i:2d}: {line}")

print("\n\nLine map:")
for out_line in sorted(result.line_map.keys()):
    in_line = result.line_map[out_line]
    print(f"Out {out_line:2d} <- In {in_line}")
