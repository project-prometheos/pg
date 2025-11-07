lines = [
    "#: of being stored in another variable, as in the first two answer rules. Either",
    "#: method is correct. Usually you would only need store the answer in a variable",
    "#: if it will be used in other places in the code as well which is not done even",
    "#: for the first two answers rules in this case.",
]

for i, line in enumerate(lines):
    stripped_for_check = line.lstrip(' \t')
    print(f"Line {i}: {repr(line)}")
    print(f"  After lstrip(' \\t'): {repr(stripped_for_check)}")
    print(f"  Starts with #: {stripped_for_check.startswith('#')}")
    print(f"  Should skip join: {not stripped_for_check.startswith('#')}")
    print()
