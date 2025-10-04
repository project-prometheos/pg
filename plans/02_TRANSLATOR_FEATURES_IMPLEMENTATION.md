# TRANSLATOR FEATURES IMPLEMENTATION PLAN

**Goal**: Complete Translator.pm feature parity in Python
**Estimated Effort**: 2-3 weeks (1 developer)
**Priority**: CRITICAL - Blocks macro loading and error handling

---

## EXECUTIVE SUMMARY

The Python translator has basic functionality but is missing critical features from Translator.pm (1,386 lines). We need to add:
- Macro loading infrastructure
- Sophisticated error handling
- Answer processing enhancements
- Problem grading system
- Post-processing hooks

**Current State**: Basic translate() pipeline (277 lines)
**Target State**: Full Translator.pm parity (1,100+ lines to add)

---

## PHASE 1: MACRO LOADING SYSTEM (Week 1, Days 1-3)

### 1.1 unrestricted_load() Implementation

**Location**: `packages/pg_translator/pg_translator/macro_loader.py`

**Reference**: Translator.pm:346-392

```python
class MacroLoader:
    """Handles loading of PG macro files with permission control."""

    def __init__(self, sandbox: PGSandbox):
        self.sandbox = sandbox
        self.loaded_files: dict[str, float] = {}  # file -> mtime
        self.init_functions: dict[str, Callable] = {}

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
        filepath = Path(filepath)
        errors = ""

        # Save current permission mask
        stored_mask = self.sandbox.get_opcode_mask()

        try:
            # Set unrestricted permissions
            self.sandbox.set_opcode_mask(OpcodeMask.EMPTY)

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
                    init_func()
                    self.init_functions[str(filepath)] = init_func
                else:
                    errors = f"Init function {init_func_name} is not callable"

        except Exception as e:
            errors = f"Error loading {filepath}: {str(e)}"

        finally:
            # Always restore mask
            self.sandbox.set_opcode_mask(stored_mask)

        return errors

    def _load_perl_macro(self, filepath: Path) -> str:
        """
        Load Perl macro file.

        Options:
        1. Convert to Python (preferred)
        2. Execute via Perl bridge
        3. Use translated version if available
        """
        # Check for pre-translated Python version
        py_version = filepath.with_suffix(".py")
        if py_version.exists():
            return self._load_python_macro(py_version)

        # For now, require manual translation
        return f"Perl macro {filepath} not yet ported to Python"

    def _load_python_macro(self, filepath: Path) -> str:
        """Load Python macro file."""
        try:
            code = filepath.read_text(encoding="utf-8")

            # Execute in sandbox namespace
            self.sandbox.exec(code, filename=str(filepath))

            # Track loaded file
            self.loaded_files[str(filepath)] = filepath.stat().st_mtime

            return ""
        except Exception as e:
            return f"Error loading {filepath}: {str(e)}\n{traceback.format_exc()}"
```

**Deliverable**: unrestricted_load() working for Python macros

---

### 1.2 PG_macro_file_eval() Implementation

**Reference**: Translator.pm:1253-1288

```python
def PG_macro_file_eval(code: str, filepath: str) -> tuple[Any, str, str]:
    """
    Evaluate macro file code with strict mode.

    Equivalent to Translator.pm:1253-1288

    Process:
    1. Add strict mode import
    2. Add file tracking for error messages
    3. Execute code in main namespace
    4. Capture output and errors
    5. Return (output, errors, full_error_report)

    Args:
        code: Macro file code
        filepath: File path for error reporting

    Returns:
        (output, errors, full_error_report)
    """
    sandbox = get_current_sandbox()

    # Track file for error messages
    eval_id = sandbox.get_next_eval_id()
    sandbox.register_file(eval_id, filepath)

    # Prepend strict mode and file tracking
    augmented_code = f"""
import strict_mode  # Equivalent to Perl strict->import
__file__ = "{filepath}"
__eval_id__ = "{eval_id}"

{code}
"""

    warnings_list = []
    output = None
    errors = ""

    # Capture warnings
    def warning_handler(message):
        warnings_list.append(str(message))

    old_warn_handler = sandbox.warning_handler
    sandbox.warning_handler = warning_handler

    try:
        # Execute in main namespace (like Perl: package main)
        output = sandbox.exec(augmented_code, filename=filepath)

        if warnings_list:
            # Process warnings through error message formatter
            formatted = PG_errorMessage("message", *warnings_list)
            # Send to outer warning handler if exists
            if old_warn_handler:
                old_warn_handler(formatted)

    except Exception as e:
        errors = str(e)

    finally:
        sandbox.warning_handler = old_warn_handler

    # Build full error report
    full_error_report = ""
    if errors:
        caller_info = traceback.extract_stack()[-2]
        full_error_report = (
            f"PG_macro_file_eval detected error at line {caller_info.lineno} "
            f"of file {caller_info.filename}\\n"
            f"{errors}\\n"
            f"The calling package is {caller_info.name}"
        )

    return (output, errors, full_error_report)
```

**Deliverable**: PG_macro_file_eval() for macro execution

---

### 1.3 Module Evaluation System

**Reference**: Translator.pm:136-183

```python
def evaluate_modules(*module_names: str) -> None:
    """
    Load Python modules into sandbox.

    Equivalent to Translator.pm:136-153

    Args:
        *module_names: Module names to load (e.g., "sympy", "numpy")
    """
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
            sandbox.included_modules.append(module_name)

        except ImportError as e:
            raise RuntimeError(f"Failed to import module {module_name}: {e}")


def load_extra_packages(*package_names: str) -> None:
    """
    Load extra packages from already-imported modules.

    Equivalent to Translator.pm:167-183
    """
    sandbox = get_current_sandbox()

    for package_name in package_names:
        package_name = package_name.removesuffix(".py")

        try:
            # Import the package
            package = importlib.import_module(package_name)

            # Add to namespace
            sandbox.namespace[package_name] = package

            # Record it
            sandbox.included_modules.append(package_name)

        except ImportError as e:
            raise RuntimeError(f"Failed to import package {package_name}: {e}")
```

**Deliverable**: Module/package loading system

---

## PHASE 2: ERROR HANDLING SYSTEM (Week 1, Days 4-5)

### 2.1 PG_errorMessage() Implementation

**Reference**: Translator.pm:533-586

```python
def PG_errorMessage(return_type: str = "traceback", *messages: str) -> str:
    """
    Format error messages with file name mapping and stack traces.

    Equivalent to Translator.pm:533-586

    Process:
    1. Join messages and clean whitespace
    2. Get file mapping from environment
    3. Replace eval IDs with filenames
    4. Add stack trace if requested
    5. Clean up paths (templates → [TMPL], etc.)

    Args:
        return_type: "message" or "traceback"
        *messages: Error messages to format

    Returns:
        Formatted error message with optional stack trace
    """
    message = "\\n".join(messages).rstrip()

    # Get file mapping
    env = get_environment()
    files = env.get_file_mapping()

    tmpl = files.get("tmpl", "$")
    root = files.get("root", "$")
    pg = files.get("pg", "$")

    # Replace directory paths with abbreviations
    message = message.replace(tmpl, "[TMPL]")
    message = message.replace(root, "[WW]")
    message = message.replace(pg, "[PG]")

    # Replace eval IDs with filenames
    # Find all (eval NNN) references
    import re
    eval_pattern = r"\\(eval (\\d+)\\)"
    for match in re.finditer(eval_pattern, message):
        eval_id = f"(eval {match.group(1)})"
        if eval_id in files:
            filename = files[eval_id]
            # Clean up filename
            filename = filename.replace(tmpl, "[TMPL]")
            filename = filename.replace(root, "[WW]")
            filename = filename.replace(pg, "[PG]")
            message = message.replace(eval_id, filename)

    # Return just message if requested or already has trace
    if return_type == "message" or "Died within" in message:
        return message + "\\n"

    # Remove trailing period for traceback
    message = message.rstrip(".")

    # Build stack trace
    trace = [message]
    skip_parser = False

    # Examine stack frames
    stack = traceback.extract_stack()
    for i, frame in enumerate(stack[2:], start=2):  # Skip this function
        func_name = frame.name

        # Stop at Safe.reval equivalent or __ANON__ (lambda)
        if func_name in ("exec", "<lambda>"):
            break

        # Skip Parser/Value calls if previous was also Parser/Value
        if skip_parser and (func_name.startswith("Parser") or func_name.startswith("Value")):
            continue

        skip_parser = func_name.startswith("Parser") or func_name.startswith("Value")

        # Skip translator internals
        if "pg_translator" in frame.filename:
            continue

        # Skip certain PG functions
        if func_name in ("safe_ev", "old_safe_ev", "ev_substring", "<lambda>"):
            continue

        # Get filename
        file = files.get(frame.filename, frame.filename)
        file = file.replace(tmpl, "[TMPL]")
        file = file.replace(root, "[WW]")
        file = file.replace(pg, "[PG]")

        trace_line = f"   from within {func_name} called at line {frame.lineno} of {file}"

        # Skip eval references
        if "(eval" not in trace_line:
            trace.append(trace_line)

    return "\\n".join(trace) + "\\n"
```

**Deliverable**: Formatted error messages with stack traces

---

### 2.2 Error Handler Integration

```python
class PGTranslator:
    """Enhanced translator with error handling."""

    def translate(self, pg_file_path: Path, seed: int, ...) -> ProblemResult:
        """Translate with comprehensive error handling."""

        # Install error handlers
        frontend_warnings = []
        backend_warnings = []

        def warning_handler(msg: str, backend: bool = False):
            if backend:
                backend_warnings.append(msg)
            else:
                frontend_warnings.append(msg)

        old_handler = self.executor.warning_handler
        self.executor.warning_handler = warning_handler

        def error_handler(msg: str):
            raise PGError(PG_errorMessage("traceback", msg))

        self.executor.error_handler = error_handler

        try:
            # Execute translation
            env = self.executor.execute(...)

            # Handle frontend warnings (always show)
            if frontend_warnings:
                formatted = PG_errorMessage("message", *frontend_warnings)
                self._handle_warning(formatted)

            # Handle backend warnings (only with debug permission)
            if backend_warnings and env.has_debug_permission():
                formatted = PG_errorMessage(
                    "message",
                    "Non fatal warnings (debugging only):",
                    *backend_warnings
                )
                self._handle_warning(formatted)

            return self._build_result(env)

        except Exception as e:
            # Format error nicely
            error_msg = PG_errorMessage("traceback", str(e))
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[error_msg]
            )

        finally:
            self.executor.warning_handler = old_handler
```

**Deliverable**: Comprehensive error handling in translator

---

## PHASE 3: ANSWER PROCESSING ENHANCEMENTS (Week 2, Days 1-3)

### 3.1 Checkbox/Radio Button Handling

**Reference**: Translator.pm:908-912

```python
def process_answers(self) -> dict[str, AnswerResult]:
    """
    Process student answers with checkbox/radio support.

    Equivalent to Translator.pm:848-959
    """
    env = self.environment
    results = {}

    for ans_name, evaluator in env.answers.items():
        # Get student response
        response = env.inputs.get(ans_name)

        # Handle checkboxes and radio buttons
        # Format: [(value, "CHECKED"), (value, ""), ...]
        if isinstance(response, list):
            if all(isinstance(item, tuple) and len(item) == 2 for item in response):
                # Extract checked values
                checked = [val for val, status in response if status == "CHECKED"]

                if len(checked) < 2:
                    # Single or no selection
                    response = checked[0] if checked else ""
                else:
                    # Multiple selections (checkbox)
                    response = checked

        # Evaluate answer
        try:
            result = evaluator.evaluate(response)
            results[ans_name] = result

        except Exception as e:
            # Create error result
            results[ans_name] = AnswerResult(
                score=0,
                correct=False,
                student_answer=str(response),
                error_message=str(e)
            )

    return results
```

**Deliverable**: Checkbox/radio button answer processing

---

### 3.2 stringify_answers() Implementation

**Reference**: Translator.pm:961-977

```python
def stringify_answers(self) -> None:
    """
    Convert all MathObject answers to strings.

    Equivalent to Translator.pm:961-977

    Ensures answer hashes contain only primitive types (str, int, float)
    for serialization.
    """
    for ans_name, result in self.answer_results.items():
        if hasattr(result, "stringify_hash"):
            # AnswerHash with stringify method
            result.stringify_hash()
        else:
            # Manual stringification
            if isinstance(result.student_answer, MathValue):
                result.student_answer = result.student_answer.to_string()

            if isinstance(result.correct_answer, MathValue):
                result.correct_answer = result.correct_answer.to_string()

            if hasattr(result, "preview_latex"):
                if isinstance(result.preview_latex, MathValue):
                    result.preview_latex = result.preview_latex.to_tex()
```

**Deliverable**: Answer stringification

---

## PHASE 4: PROBLEM GRADING SYSTEM (Week 2, Days 4-5)

### 4.1 Grader Plugin Architecture

**Reference**: Translator.pm:1009-1142

```python
from typing import Protocol

class ProblemGrader(Protocol):
    """Protocol for problem graders."""

    def __call__(
        self,
        answers: dict[str, AnswerResult],
        problem_state: dict[str, Any],
        **options: Any
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Grade problem.

        Args:
            answers: Answer results
            problem_state: Current problem state
            **options: Grading options

        Returns:
            (problem_result, updated_state)
        """
        ...


def std_problem_grader(
    answers: dict[str, AnswerResult],
    problem_state: dict[str, Any],
    **options: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Standard all-or-nothing grader.

    Equivalent to Translator.pm:1014-1068

    Returns score of 1 if all answers correct, 0 otherwise.
    """
    # Copy state (don't modify input)
    state = dict(problem_state)

    # Initialize result
    result = {
        "score": 0,
        "errors": "",
        "type": "std_problem_grader",
        "msg": ""
    }

    # Check if we have answers
    if not answers:
        result["msg"] = "This problem did not ask any questions."
        return (result, state)

    # Multi-answer message
    if len(answers) > 1:
        result["msg"] = "In order to get credit for this problem all answers must be correct."

    # Only grade if answers submitted
    if not options.get("answers_submitted"):
        return (result, state)

    # Check all answers
    all_correct = True
    for ans_name, answer in answers.items():
        if answer.score != 1:
            all_correct = False
            break

    # Set score
    result["score"] = 1 if all_correct else 0

    # Update state
    state["recorded_score"] = state.get("recorded_score", 0)
    if all_correct or state["recorded_score"] == 1:
        state["recorded_score"] = 1
    else:
        state["recorded_score"] = 0

    # Update attempt counters
    if all_correct:
        state["num_of_correct_ans"] = state.get("num_of_correct_ans", 0) + 1
    else:
        state["num_of_incorrect_ans"] = state.get("num_of_incorrect_ans", 0) + 1

    return (result, state)


def avg_problem_grader(
    answers: dict[str, AnswerResult],
    problem_state: dict[str, Any],
    **options: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Average (partial credit) grader.

    Equivalent to Translator.pm:1075-1142

    Returns weighted average of answer scores.
    """
    state = dict(problem_state)

    result = {
        "score": 0,
        "errors": "",
        "type": "avg_problem_grader",
        "msg": ""
    }

    # Multi-answer message
    if len(answers) > 1:
        result["msg"] = "You can earn partial credit on this problem."

    # Only grade if submitted
    if not options.get("answers_submitted"):
        return (result, state)

    # Calculate credit for each answer
    credit = {}
    for ans_name, answer in answers.items():
        credit[ans_name] = answer.score

    # Handle optional answers (credit from other answers)
    for ans_name, answer in answers.items():
        if credit[ans_name] == 1 and hasattr(answer, "credit_from"):
            # Give credit to related optional answers if blank
            credit_list = answer.credit_from
            if not isinstance(credit_list, list):
                credit_list = [credit_list]

            for credit_name in credit_list:
                if credit_name in answers:
                    student_ans = answers[credit_name].student_answer
                    if not student_ans or student_ans.strip() == "":
                        credit[credit_name] = 1
                        answers[credit_name].ans_message = (
                            "This answer was marked correct because the primary answer is correct."
                        )

    # Calculate weighted average
    total_weight = 0
    total_score = 0

    for ans_name, answer in answers.items():
        weight = getattr(answer, "weight", 1)
        total_weight += weight
        total_score += weight * credit[ans_name]

    result["score"] = total_score / total_weight if total_weight > 0 else 0

    # Update state
    state["num_of_correct_ans"] = state.get("num_of_correct_ans", 0)
    state["num_of_incorrect_ans"] = state.get("num_of_incorrect_ans", 0)

    if total_score == total_weight:
        state["num_of_correct_ans"] += 1
    elif total_score < total_weight:
        state["num_of_incorrect_ans"] += 1

    state["recorded_score"] = max(
        state.get("recorded_score", 0),
        result["score"]
    )

    return (result, state)
```

**Deliverable**: Grader system with std and avg graders

---

## PHASE 5: POST-PROCESSING HOOKS (Week 3, Days 1-3)

### 5.1 Content Post-Processor System

**Reference**: Translator.pm:1165-1207

```python
class ContentPostProcessor:
    """Manages content post-processing hooks."""

    def __init__(self):
        self.processors: list[Callable] = []

    def add_processor(self, processor: Callable) -> None:
        """Add a post-processor hook."""
        self.processors.append(processor)

    def process(
        self,
        problem_text: str,
        header_text: str,
        display_mode: str,
        problem_result: dict[str, Any]
    ) -> tuple[str, str]:
        """
        Run all post-processors.

        Args:
            problem_text: Problem HTML/TeX
            header_text: Header HTML
            display_mode: "HTML", "TeX", or "PTX"
            problem_result: Grading result

        Returns:
            (processed_problem_text, processed_header_text)
        """
        if display_mode == "TeX":
            # TeX mode: pass text reference to processors
            text_ref = {"text": problem_text}

            for processor in self.processors:
                try:
                    processor(text_ref)
                except Exception as e:
                    logger.error(f"Post-processor error: {e}")

            return (text_ref["text"], header_text)

        else:
            # HTML/PTX: use DOM manipulation
            from lxml import html as lxml_html

            problem_dom = lxml_html.fromstring(problem_text)
            header_dom = lxml_html.fromstring(header_text)

            for processor in self.processors:
                try:
                    processor(problem_dom, header_dom, problem_result)
                except Exception as e:
                    logger.error(f"Post-processor error: {e}")

            return (
                lxml_html.tostring(problem_dom, encoding="unicode"),
                lxml_html.tostring(header_dom, encoding="unicode")
            )


def add_content_post_processor(processor: Callable) -> None:
    """
    Add a content post-processor hook.

    Usage in PG problems:
        add_content_post_processor(lambda dom, header, result: ...)
    """
    env = get_environment()
    if not hasattr(env, "post_processors"):
        env.post_processors = ContentPostProcessor()

    env.post_processors.add_processor(processor)
```

**Example Post-Processor**:
```python
def add_warning_style(problem_dom, header_dom, result):
    """Add warning styling to incorrect answers."""
    if result.get("score", 1) < 1:
        # Add warning class to problem
        problem_dom.set("class",
            problem_dom.get("class", "") + " has-incorrect-answers"
        )

        # Add CSS to header
        style = html.Element("style")
        style.text = """
        .has-incorrect-answers {
            border-left: 4px solid orange;
            padding-left: 1em;
        }
        """
        header_dom.append(style)
```

**Deliverable**: Post-processing hook system

---

## INTEGRATION & TESTING

### Integration with Existing Translator

```python
class PGTranslator:
    """Enhanced translator with all features."""

    def __init__(self):
        self.preprocessor = PGPreprocessor()
        self.executor = PGExecutor()
        self.macro_loader = MacroLoader(self.executor.sandbox)
        self.grader = std_problem_grader
        self.post_processor = ContentPostProcessor()

        # Load core macros automatically
        self.macro_loader.unrestricted_load("PG.pl")

    def translate(
        self,
        pg_file_path: Path,
        seed: int,
        inputs: dict[str, str] | None = None,
        grader: ProblemGrader | None = None
    ) -> ProblemResult:
        """Full translation with all features."""

        # 1. Preprocess
        preprocessed = self.preprocessor.preprocess(pg_source)

        # 2. Execute with error handling
        env = self._execute_with_error_handling(preprocessed.code, seed)

        # 3. Process answers
        answer_results = self.process_answers(env, inputs)

        # 4. Grade problem
        problem_result, problem_state = (grader or self.grader)(
            answer_results,
            env.problem_state,
            answers_submitted=(inputs is not None)
        )

        # 5. Stringify answers
        self.stringify_answers(answer_results)

        # 6. Post-process content
        problem_text, header_text = self.post_processor.process(
            env.render_text(),
            env.render_header(),
            env.display_mode,
            problem_result
        )

        return ProblemResult(
            statement_html=problem_text,
            header_html=header_text,
            answer_blanks={...},
            answer_results=answer_results,
            score=problem_result["score"],
            ...
        )
```

---

## DELIVERABLES & MILESTONES

### Week 1 Milestones:
- ✅ Day 3: Macro loading (unrestricted_load, PG_macro_file_eval)
- ✅ Day 5: Error handling (PG_errorMessage, handlers)

### Week 2 Milestones:
- ✅ Day 3: Answer processing (checkboxes, stringify)
- ✅ Day 5: Grading system (std_grader, avg_grader)

### Week 3 Milestones:
- ✅ Day 3: Post-processing hooks
- ✅ Day 5: Full integration and testing

---

## SUCCESS CRITERIA

1. **Functional**:
   - Macro loading works for .py macros
   - Error messages show proper file names and traces
   - Checkboxes/radio buttons process correctly
   - Both graders work and support partial credit
   - Post-processing hooks modify content

2. **Quality**:
   - 90% test coverage
   - All translator tests pass
   - Error messages match Perl format

3. **Performance**:
   - Macro loading <50ms per file
   - Error handling adds <10ms overhead

---

**End of Translator Features Implementation Plan**
