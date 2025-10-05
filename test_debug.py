import sys
sys.path.insert(0, 'packages/pg_macros')

from pg_macros.core import pg_core

envir = {"problemSeed": 123, "displayMode": "HTML"}
env = pg_core.PGEnvironment(envir)
pg_core.set_environment(env)

pg_core.TEXT("Hello ", "World")
pg_core.TEXT("Problem text here")

text = env.get_text()
print(f"Text: '{text}'")
print(f"Length: {len(text)}")
print(f"Output array: {env.output_array}")
