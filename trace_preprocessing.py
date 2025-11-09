import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))

from pg_translator.pg_preprocessor_pygment import PGPreprocessor

# Read just lines 35-42
source_lines = [
    "Context()->variables->add(t => 'Real');",
    "@tvals     = ('pi/12',   'pi/6',   '5pi/12',   'pi/3',   '2pi/3',   '7pi/12');",
    "@tvals_tex = ('\\pi/12', '\\pi/6', '5\\pi/12', '\\pi/3', '2\\pi/3', '7\\pi/12');",
    "$n         = random(1, $#tvals);",
    "$x         = Compute('2sin(2t)');",
    "$x0        = $x->eval(t => $tvals[$n]);",
    "$y         = Compute('2sin(3t)');",
    "$y0        = $y->eval(t => $tvals[$n]);",
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
