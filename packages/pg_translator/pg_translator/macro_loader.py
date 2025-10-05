"""
Macro Loading System for PG Translator.

Handles loading and caching of PG macro files (.py and .pl) with permission control.
Reference: Translator.pm:346-392, 1253-1288
"""

from __future__ import annotations

import importlib.util
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from .sandbox import Sandbox


class OpcodeMask:
    """Opcode permission masks for sandbox."""

    EMPTY = set()  # Allow all operations
    RESTRICTED = {  # Default restricted operations
        "eval",
        "exec",
        "compile",
        "open",
        "__import__",
    }


class MacroLoader:
    """
    Handles loading of PG macro files with permission control.

    Equivalent to Translator.pm unrestricted_load() and PG_macro_file_eval()
    """

    def __init__(self, sandbox: Sandbox):
        """
        Initialize macro loader.

        Args:
            sandbox: PGSandbox instance for code execution
        """
        self.sandbox = sandbox
        self.loaded_files: dict[str, float] = {}  # filepath -> mtime
        self.init_functions: dict[str, Callable] = {}  # filepath -> init func
        self.search_paths: list[Path] = []

        # Set default search paths
        self._setup_search_paths()

    def _setup_search_paths(self) -> None:
        """Setup macro search paths."""
        # Try to find macros directory
        repo_root = Path(__file__).parent.parent.parent.parent
        macros_dir = repo_root / "macros"

        if macros_dir.exists():
            self.search_paths.append(macros_dir)
            self.search_paths.append(macros_dir / "core")

        # Python macro directory
        pg_macros_dir = repo_root / "packages" / "pg_macros"
        if pg_macros_dir.exists():
            self.search_paths.append(pg_macros_dir)
            self.search_paths.append(pg_macros_dir / "core")

    def find_macro(self, macro_name: str) -> Path | None:
        """
        Find macro file in search paths.

        Args:
            macro_name: Macro name (e.g., "PG.pl" or "pg_core")

        Returns:
            Path to macro file, or None if not found
        """
        # Try as-is first
        macro_path = Path(macro_name)
        if macro_path.exists():
            return macro_path

        # Try in search paths
        for search_path in self.search_paths:
            # Try exact name
            candidate = search_path / macro_name
            if candidate.exists():
                return candidate

            # Try with .py extension
            if not macro_name.endswith(".py"):
                candidate = search_path / f"{macro_name}.py"
                if candidate.exists():
                    return candidate

            # Try with .pl extension
            if not macro_name.endswith(".pl"):
                candidate = search_path / f"{macro_name}.pl"
                if candidate.exists():
                    return candidate

        return None

    def unrestricted_load(self, filepath: str | Path) -> str:
        """
        Load macro file with unrestricted permissions.

        Equivalent to Translator.pm:346-392

        Process:
        1. Save current opcode mask
        2. Set mask to empty (allow all operations)
        3. Load file with rdo() equivalent
        4. Look for _<name>_init() function
        5. Call init function if found
        6. Restore original mask

        Args:
            filepath: Path to macro file (.pl or .py)

        Returns:
            Error string if any, empty otherwise
        """
        # Find file
        if isinstance(filepath, str):
            found_path = self.find_macro(filepath)
            if found_path is None:
                return f"Cannot find macro file: {filepath}"
            filepath = found_path
        else:
            filepath = Path(filepath)

        if not filepath.exists():
            return f"Macro file does not exist: {filepath}"

        errors = ""

        # Save current permission mask
        stored_mask = self.sandbox.get_restricted_names()

        try:
            # Set unrestricted permissions (empty mask = allow all)
            self.sandbox.set_restricted_names(OpcodeMask.EMPTY)

            # Get macro file name for init function
            macro_name = filepath.stem  # "PG" from "PG.pl"
            init_func_name = f"_{macro_name}_init"

            # Check if already loaded and has init function
            if init_func_name in self.sandbox.namespace:
                init_func = self.sandbox.namespace[init_func_name]
                if callable(init_func):
                    # Already loaded, just call init
                    init_func()
                    self.init_functions[str(filepath)] = init_func
                    return ""

            # Load the file
            if filepath.suffix == ".pl":
                errors = self._load_perl_macro(filepath)
            elif filepath.suffix == ".py":
                errors = self._load_python_macro(filepath)
            else:
                errors = f"Unknown macro file type: {filepath}"

            if errors:
                return errors

            # Look for init function
            if init_func_name in self.sandbox.namespace:
                init_func = self.sandbox.namespace[init_func_name]
                if callable(init_func):
                    # Call initialization
                    try:
                        init_func()
                        self.init_functions[str(filepath)] = init_func
                    except Exception as e:
                        errors = f"Error calling {init_func_name}: {e}"
                else:
                    errors = f"Init function {init_func_name} is not callable"

        except Exception as e:
            errors = f"Error loading {filepath}: {str(e)}\n{traceback.format_exc()}"

        finally:
            # Always restore mask
            self.sandbox.set_restricted_names(stored_mask)

        return errors

    def _load_perl_macro(self, filepath: Path) -> str:
        """
        Load Perl macro file.

        For now, Perl macros must be manually ported to Python.
        Future: Could use Perl bridge or automated conversion.

        Args:
            filepath: Path to .pl file

        Returns:
            Error message or empty string
        """
        # Check for pre-translated Python version
        py_version = filepath.with_suffix(".py")
        if py_version.exists():
            return self._load_python_macro(py_version)

        # Look for Python version in pg_macros
        py_name = filepath.stem
        for search_path in self.search_paths:
            py_candidate = search_path / f"{py_name}.py"
            if py_candidate.exists():
                return self._load_python_macro(py_candidate)

        # Not yet ported
        return f"Perl macro {filepath.name} not yet ported to Python. Please create Python version."

    def _load_python_macro(self, filepath: Path) -> str:
        """
        Load Python macro file.

        Args:
            filepath: Path to .py file

        Returns:
            Error message or empty string
        """
        try:
            code = filepath.read_text(encoding="utf-8")

            # Execute in sandbox namespace
            self.sandbox.exec(code, filename=str(filepath))

            # Track loaded file
            self.loaded_files[str(filepath)] = filepath.stat().st_mtime

            return ""

        except Exception as e:
            return f"Error loading {filepath}: {str(e)}\n{traceback.format_exc()}"

    def load_macro(self, macro_name: str, unrestricted: bool = False) -> None:
        """
        Load a macro file.

        Args:
            macro_name: Name of macro (e.g., "PGstandard.pl")
            unrestricted: If True, load with full permissions

        Raises:
            RuntimeError: If macro cannot be loaded
        """
        if unrestricted:
            errors = self.unrestricted_load(macro_name)
        else:
            # Find and load with restrictions
            filepath = self.find_macro(macro_name)
            if filepath is None:
                raise RuntimeError(f"Cannot find macro: {macro_name}")

            if filepath.suffix == ".py":
                errors = self._load_python_macro(filepath)
            else:
                errors = self._load_perl_macro(filepath)

        if errors:
            raise RuntimeError(f"Failed to load macro {macro_name}: {errors}")

    def load_macros(self, *macro_names: str) -> None:
        """
        Load multiple macros.

        Equivalent to loadMacros() in PG.pl

        Args:
            *macro_names: Macro names to load

        Raises:
            RuntimeError: If any macro fails to load
        """
        for name in macro_names:
            self.load_macro(name)


def PG_macro_file_eval(
    code: str,
    filepath: str,
    sandbox: Sandbox
) -> tuple[Any, str, str]:
    """
    Evaluate macro file code with strict mode.

    Equivalent to Translator.pm:1253-1288

    Process:
    1. Add file tracking for error messages
    2. Execute code in sandbox namespace
    3. Capture output and errors
    4. Return (output, errors, full_error_report)

    Args:
        code: Macro file code
        filepath: File path for error reporting
        sandbox: Sandbox for execution

    Returns:
        (output, errors, full_error_report)
    """
    # Track file for error messages
    eval_id = f"eval_{id(code)}"
    sandbox.register_file(eval_id, filepath)

    # Prepend file tracking
    augmented_code = f'''
# File: {filepath}
__file__ = {filepath!r}
__eval_id__ = {eval_id!r}

{code}
'''

    warnings_list: list[str] = []
    output = None
    errors = ""

    # Capture warnings (if warning system exists)
    def warning_handler(message: str) -> None:
        warnings_list.append(str(message))

    old_warn_handler = getattr(sandbox, "warning_handler", None)
    sandbox.warning_handler = warning_handler  # type: ignore

    try:
        # Execute in sandbox namespace
        output = sandbox.exec(augmented_code, filename=filepath)

        if warnings_list:
            # Process warnings through error message formatter
            from .error_handler import PG_errorMessage

            formatted = PG_errorMessage("message", *warnings_list)
            # Send to outer warning handler if exists
            if old_warn_handler and callable(old_warn_handler):
                old_warn_handler(formatted)

    except Exception as e:
        errors = str(e)
        errors += f"\n{traceback.format_exc()}"

    finally:
        if old_warn_handler is not None:
            sandbox.warning_handler = old_warn_handler  # type: ignore

    # Build full error report
    full_error_report = ""
    if errors:
        stack = traceback.extract_stack()
        if stack:
            caller_info = stack[-2]
            full_error_report = (
                f"PG_macro_file_eval detected error at line {caller_info.lineno} "
                f"of file {caller_info.filename}\n"
                f"{errors}\n"
                f"The calling context is {caller_info.name}"
            )

    return (output, errors, full_error_report)


def evaluate_modules(*module_names: str, sandbox: Sandbox | None = None) -> None:
    """
    Load Python modules into sandbox.

    Equivalent to Translator.pm:136-153

    Args:
        *module_names: Module names to load (e.g., "sympy", "numpy")
        sandbox: Sandbox instance (uses current if None)
    """
    if sandbox is None:
        from .executor import get_current_sandbox
        sandbox = get_current_sandbox()

    for module_name in module_names:
        # Remove .py extension if present
        module_name = module_name.removesuffix(".py")

        try:
            # Import module
            module = importlib.import_module(module_name)

            # Share module with sandbox
            sandbox.namespace[module_name] = module

            # Record in included modules
            if not hasattr(sandbox, "included_modules"):
                sandbox.included_modules = []  # type: ignore
            sandbox.included_modules.append(module_name)  # type: ignore

        except ImportError as e:
            raise RuntimeError(f"Failed to import module {module_name}: {e}")


def load_extra_packages(*package_names: str, sandbox: Sandbox | None = None) -> None:
    """
    Load extra packages from already-imported modules.

    Equivalent to Translator.pm:167-183

    Args:
        *package_names: Package names to load
        sandbox: Sandbox instance (uses current if None)
    """
    evaluate_modules(*package_names, sandbox=sandbox)
