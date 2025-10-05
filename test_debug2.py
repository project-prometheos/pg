import sys
sys.path.insert(0, 'packages/pg_macros')

from pg_macros.core import pg_core

envir = {"problemSeed": 123}
env = pg_core.PGEnvironment(envir)
pg_core.set_environment(env)

evaluator1 = {"type": "numeric", "correct": 42}
evaluator2 = {"type": "numeric", "correct": 17}

pg_core.ANS(evaluator1, evaluator2)

print(f"Answers hash: {env.answers_hash}")
print(f"Answer entry order: {env.answer_entry_order}")
print(f"Answer blank queue: {env.answer_blank_queue}")
print(f"Length: {len(env.answers_hash)}")
