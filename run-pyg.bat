@echo off
REM Run a standalone .pyg file with proper PYTHONPATH setup
REM Usage: run-pyg.bat problem.pyg

setlocal
set PYTHONPATH=%~dp0packages;%~dp0packages\pg_math;%~dp0packages\pg_pgml;%~dp0packages\pg_parser;%~dp0packages\pg_answer;%~dp0packages\pg_renderer;%~dp0packages\pg_macros
python %*
endlocal

