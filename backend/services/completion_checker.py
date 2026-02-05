# Checks run completion: polls or listens for job/workflow completion and updates state.

import ast
import json
import re
from typing import Any


def _check_contains(output: str, completion_value: str) -> dict[str, Any]:
    """Output must include the given string."""
    if not completion_value:
        return {"success": True, "reason": "No value to check (empty contains)."}
    if completion_value in output:
        return {"success": True, "reason": "Output contains the required string."}
    return {"success": False, "reason": f"Output does not contain required string: {repr(completion_value[:50])}..."}


def _check_regex(output: str, completion_value: str) -> dict[str, Any]:
    """Output must match the given regex pattern."""
    if not completion_value:
        return {"success": True, "reason": "No pattern to check (empty regex)."}
    try:
        pattern = re.compile(completion_value)
    except re.error as e:
        return {"success": False, "reason": f"Invalid regex pattern: {e}"}
    if pattern.search(output) is not None:
        return {"success": True, "reason": "Output matches the required regex."}
    return {"success": False, "reason": f"Output does not match regex: {repr(completion_value[:50])}..."}


def _check_json(output: str, _completion_value: str) -> dict[str, Any]:
    """Output must be valid JSON. completion_value is unused for validation."""
    output_stripped = output.strip()
    if not output_stripped:
        return {"success": False, "reason": "Output is empty."}
    try:
        json.loads(output_stripped)
        return {"success": True, "reason": "Output is valid JSON."}
    except json.JSONDecodeError as e:
        return {"success": False, "reason": f"Output is not valid JSON: {e}"}


def _has_function_definition(tree: ast.AST) -> bool:
    """Return True if the AST contains at least one function definition."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return True
    return False


def _extract_code_blocks(text: str) -> list[str]:
    """Extract content from ```...``` or ```python...``` blocks."""
    blocks: list[str] = []
    # Match ```optional_lang\ncontent```
    pattern = re.compile(r"```(?:\w*\n)?(.*?)```", re.DOTALL)
    for match in pattern.finditer(text):
        blocks.append(match.group(1).strip())
    return blocks


def _check_python_function(output: str, _completion_value: str) -> dict[str, Any]:
    """Output must contain a valid Python function definition."""
    candidates: list[str] = [output.strip()]
    candidates.extend(_extract_code_blocks(output))

    for code in candidates:
        if not code or "def " not in code:
            continue
        try:
            tree = ast.parse(code)
            if _has_function_definition(tree):
                return {"success": True, "reason": "Output contains a valid Python function definition."}
        except SyntaxError:
            continue

    # Try parsing the whole output as a single module (e.g. just "def foo(): pass")
    try:
        tree = ast.parse(output)
        if _has_function_definition(tree):
            return {"success": True, "reason": "Output contains a valid Python function definition."}
    except SyntaxError:
        pass

    return {"success": False, "reason": "Output does not contain a valid Python function definition."}


_CHECKERS: dict[str, callable] = {
    "contains": _check_contains,
    "regex": _check_regex,
    "json": _check_json,
    "python_function": _check_python_function,
}


def check_completion(
    output: str,
    completion_type: str,
    completion_value: str | None,
) -> dict[str, Any]:
    """
    Check whether the output satisfies the completion criteria.

    Supported completion_type values:
    - "contains": output must include the string in completion_value.
    - "regex": output must match the regex pattern in completion_value.
    - "json": output must be valid JSON (completion_value ignored).
    - "python_function": output must contain a valid Python function definition (completion_value ignored).
    - Empty/None: no validation, always succeeds.

    Returns:
        {"success": bool, "reason": str}
    """
    if output is None:
        output = ""
    completion_value = completion_value or ""

    # If no completion type specified, validation passes automatically
    if not completion_type or completion_type.strip() == "":
        return {
            "success": True,
            "reason": "No completion validation specified.",
        }

    checker = _CHECKERS.get(completion_type)
    if checker is None:
        # Treat unknown types as "no validation" for backwards compatibility
        return {
            "success": True,
            "reason": f"Unknown completion_type '{completion_type}' - treating as no validation. Supported types: contains, regex, json, python_function.",
        }

    return checker(output, completion_value)
