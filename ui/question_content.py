"""Question typing, answer comparison and solution text.

Kept free of Qt so the practice page stays a thin orchestrator and this logic
can be tested directly.
"""
import json
import re
import textwrap

from core.i18n import tr

PAP = "pap"
BATCH = "batch"
CSHARP = "csharp_practice"
CODE = "code"
INTERACTIVE = "interactive"
TABLE = "table"
TEXT = "text"

CODE_MODES = (CODE, BATCH, CSHARP)
CODE_TYPES = ("code", "batch", "csharp_practice")
INTERACTIVE_TYPES = ("multi_select", "ordering", "matching", "table_sort")
AE_CODE_PATTERN = re.compile(
    r"\b(?:static\s+void\s+Main|Console\.|using\s+System|class\s+\w+)\b"
)


def parse_answer(raw):
    """Decode a stored answer, returning None when it is not JSON."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def has_tables(data):
    """True when an answer is rendered as one or more tables."""
    return isinstance(data, dict) and (
        ("headers" in data and "rows" in data)
        or isinstance(data.get("tables"), list)
    )


def question_mode(question_type, subject_name, question_text, template=None):
    """Pick the answer view for a question, in the same order the page used."""
    if question_type == PAP:
        return PAP
    if question_type in CODE_TYPES:
        return question_type
    if subject_name == "AE" and AE_CODE_PATTERN.search(question_text or ""):
        return CODE
    if question_type in INTERACTIVE_TYPES:
        return INTERACTIVE
    if template is not None and has_tables(template):
        return TABLE
    return TEXT


def split_code_question(question_text):
    """Separate the fixed Main method shell from its editable body."""
    lines = question_text.splitlines()
    main_index = next(
        (
            index for index, line in enumerate(lines)
            if re.search(r"\bstatic\s+void\s+Main\s*\(", line)
        ),
        None,
    )
    if main_index is None:
        return question_text.strip(), "", "", ""

    prompt = "\n".join(lines[:main_index]).strip()
    signature = lines[main_index].strip()
    opening_index = next(
        (index for index in range(main_index + 1, len(lines)) if "{" in lines[index]),
        None,
    )
    if opening_index is None:
        return prompt, signature, "", ""

    prefix = signature + "\n" + lines[opening_index].strip()
    depth = lines[opening_index].count("{") - lines[opening_index].count("}")
    closing_index = None
    for index in range(opening_index + 1, len(lines)):
        depth += lines[index].count("{") - lines[index].count("}")
        if depth <= 0:
            closing_index = index
            break

    if closing_index is None:
        body_lines = lines[opening_index + 1:]
        suffix = ""
    else:
        body_lines = lines[opening_index + 1:closing_index]
        suffix = lines[closing_index].strip()

    body = "\n".join(body_lines).strip("\n")
    return prompt, prefix, body, suffix


def format_code_body(code):
    """Indent a solution as a body inside the fixed Main method."""
    body = textwrap.dedent((code or "").strip("\n"))
    if not body:
        return ""
    return "\n".join(
        ("        " + line if line.strip() else "")
        for line in body.splitlines()
    )


def compact(text):
    """Drop all whitespace so 'alter>=18' and 'alter >= 18' compare equal."""
    return re.sub(r"\s+", "", text or "")


def normalize_console(text):
    """Compare console output without trailing whitespace or blank-line noise."""
    return "\n".join(
        line.rstrip() for line in text.replace("\r", "").strip().splitlines()
    )


def condition_answer_matches(entered, expected):
    """Check the condition entered into the supplied if-statement scaffold."""
    match = re.search(r"\bif\s*\(\s*(.*?)\s*\)", entered or "", re.DOTALL)
    if not match:
        return False
    return compact(match.group(1)) == compact(expected)


def code_answer_matches(entered, expected, alternatives=()):
    """Compare code while ignoring indentation differences."""
    submitted = textwrap.dedent(
        (entered or "").replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    ).rstrip()
    if not submitted:
        return False

    for candidate in (expected, *alternatives):
        target = textwrap.dedent(format_code_body(candidate)).rstrip()
        if target and submitted == target:
            return True
    return False


def format_solution_text(question, data, mode, interactive_kind=None):
    """Build the reference answer shown when the user reveals it."""
    raw = question["answer"]

    if mode == PAP and isinstance(data, dict):
        nodes = {node.get("id"): node for node in data.get("nodes", [])}
        lines = [tr("Flowchart blocks:")]
        for node in data.get("nodes", []):
            lines.append(f'- {node.get("type", "Block")}: {node.get("text", "")}')
        lines.extend(("", tr("Connections:")))
        for edge in data.get("edges", []):
            source = nodes.get(edge.get("from"), {})
            target = nodes.get(edge.get("to"), {})
            lines.append(
                f'- {source.get("text", edge.get("from"))} '
                f'--[{edge.get("label", "Normal")}]--> '
                f'{target.get("text", edge.get("to"))}'
            )
        return "\n".join(lines)

    if mode == INTERACTIVE and isinstance(data, dict):
        if interactive_kind == "multi_select":
            options, correct = data.get("options", []), data.get("correct", [])
            return tr("Correct options:") + "\n" + "\n".join(
                f"✓ {options[index]}"
                for index in correct
                if isinstance(index, int) and 0 <= index < len(options)
            )
        if interactive_kind == "ordering":
            return tr("Correct order:") + "\n" + "\n".join(
                f"{index + 1}. {value}"
                for index, value in enumerate(data.get("items", []))
            )
        if interactive_kind == "matching":
            return tr("Correct matches:") + "\n" + "\n".join(
                f'{pair.get("left", "")}  →  {pair.get("right", "")}'
                for pair in data.get("pairs", [])
            )
        if interactive_kind == "table_sort":
            categories, cards = data.get("categories", []), data.get("cards", [])
            return tr("Correct categories:") + "\n" + "\n".join(
                f"{category}: " + ", ".join(
                    str(card.get("text", ""))
                    for card in cards
                    if str(card.get("category", "")) == str(category)
                )
                for category in categories
            )

    if mode == BATCH and isinstance(data, dict):
        solution = data.get("solution", "")
        output = data.get("expected_output", [])
        output_text = "\n".join(output) if isinstance(output, list) else str(output)
        return (
            f"{tr('Solution:')}\n{solution}\n\n"
            f"{tr('Expected output:')}\n{output_text}"
        ).strip()

    if mode == CSHARP and isinstance(data, dict):
        solution = format_code_body(data.get("solution", ""))
        output = data.get("output", "")
        return (
            f"{tr('Solution:')}\n{solution}\n\n{tr('Console output:')}\n{output}"
        ).strip()

    if mode == CODE:
        solution = data.get("solution", raw) if isinstance(data, dict) else raw
        return format_code_body(solution)
    if isinstance(data, dict) and "solution" in data:
        return str(data["solution"])
    return str(raw)
