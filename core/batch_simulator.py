"""Safe, deliberately small simulator for the Batch commands used in exercises.

This module interprets a whitelist of commands. It never invokes a shell, subprocess,
or operating-system command.
"""
import ast
import operator
import re


class BatchSimulationError(ValueError):
    pass


_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _arithmetic(expression):
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            return _UNARY[type(node.op)](visit(node.operand))
        raise BatchSimulationError("Unsupported arithmetic expression.")

    return visit(tree)


def simulate_batch(source, inputs=()):
    """Return simulated console output and state for a safe Batch subset."""
    variables = {}
    output = []
    input_values = iter(inputs)
    echo_enabled = True
    color = None
    lines = source.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    index = 0
    steps = 0

    def expand(value):
        return re.sub(
            r"%([^%]+)%",
            lambda match: variables.get(match.group(1).upper(), match.group(0)),
            value,
        )

    while index < len(lines):
        steps += 1
        if steps > 500:
            raise BatchSimulationError("Simulation stopped: command limit reached.")
        raw = lines[index].strip()
        index += 1
        if not raw or raw.startswith("::") or raw.upper().startswith("REM "):
            continue
        raw = raw.lstrip("@")
        upper = raw.upper()
        if upper == "ECHO OFF":
            echo_enabled = False
            continue
        if upper == "ECHO ON":
            echo_enabled = True
            continue
        if upper.startswith("ECHO "):
            value = expand(raw[5:])
            output.append("" if value == "." else value)
            continue
        if upper == "ECHO.":
            output.append("")
            continue
        if upper.startswith("SET /P "):
            match = re.match(r"(?i)^SET\s+/P\s+([A-Za-z_][\w]*)\s*=\s*(.*)$", raw)
            if not match:
                raise BatchSimulationError("Invalid SET /P syntax.")
            name, prompt = match.groups()
            output.append(expand(prompt))
            try:
                variables[name.upper()] = str(next(input_values))
            except StopIteration:
                raise BatchSimulationError(f"Input required for variable {name}.")
            continue
        if upper.startswith("SET /A "):
            expression = raw[7:].strip()
            if "=" in expression:
                name, expression = expression.split("=", 1)
                name = name.strip()
            else:
                name = None
            expression = expand(expression).replace("%", "")
            result = _arithmetic(expression)
            if name:
                variables[name.upper()] = str(result)
            else:
                output.append(str(result))
            continue
        if upper.startswith("SET "):
            match = re.match(r"(?i)^SET\s+([A-Za-z_][\w]*)=(.*)$", raw)
            if not match:
                raise BatchSimulationError("Invalid SET syntax.")
            name, value = match.groups()
            variables[name.upper()] = expand(value)
            continue
        if upper.startswith("IF "):
            match = re.match(
                r'(?is)^IF\s+(?:/I\s+)?["]?(.+?)["]?\s*==\s*["]?(.+?)["]?\s*\(\s*(.*?)\s*\)\s*$',
                raw,
            )
            if not match:
                raise BatchSimulationError("Supported IF syntax: IF /I \"%VAR%\" == \"value\" (command).")
            left, right, command = match.groups()
            insensitive = bool(re.match(r"(?i)^IF\s+/I", raw))
            left, right = expand(left.strip().strip('"')), expand(right.strip().strip('"'))
            equal = left.casefold() == right.casefold() if insensitive else left == right
            if equal:
                lines.insert(index, command)
            continue
        if upper.startswith("COLOR "):
            color = raw[6:].strip().upper()
            if not re.fullmatch(r"[0-9A-F]{1,2}", color):
                raise BatchSimulationError("COLOR expects one or two hexadecimal digits.")
            continue
        if upper == "PAUSE":
            output.append("Drücken Sie eine beliebige Taste . . .")
            continue
        raise BatchSimulationError(f"Unsupported command: {raw}")

    return {"output": "\n".join(output), "variables": variables, "color": color}
