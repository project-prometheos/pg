#!/usr/bin/env python3
import sys
sys.path.insert(0, 'packages/pg_translator')

# Force reload
if 'pg_translator.in_process_sandbox' in sys.modules:
    del sys.modules['pg_translator.in_process_sandbox']

from pg_translator.in_process_sandbox import InProcessSandbox

sb = InProcessSandbox()
sb.initialize_environment(1234)

print('Keys with "parser" in them:')
for key in sb.namespace.keys():
    if 'parser' in key.lower():
        print(f'  {key}')
        
print(f'\nTotal keys: {len(sb.namespace)}')
print(f'\nparserFunction in namespace: {"parserFunction" in sb.namespace}')
