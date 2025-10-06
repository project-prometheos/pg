# PG Macro Port Plan

[[BT]][[BT]][[BT]]sh
mkdir -p packages/pg_macros/pg_macros/runtime packages/pg_macros/tests/golden
cat <<"EOF" > packages/pg_macros/pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
