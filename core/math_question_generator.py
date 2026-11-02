"""Generate fresh, table-based math questions on demand."""
import json
import random

from database.question_repository import QuestionRepository

DIGITS = "0123456789ABCDEF"
BASE_NAMES = {2: "Binary", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}
CONVERSION_PAIRS = [(s, t) for s in (2, 8, 10, 16) for t in (2, 8, 10, 16) if s != t]
MATH_QUESTION_TYPES = [
    (f"convert_{source}_{target}", f"{BASE_NAMES[source]} → {BASE_NAMES[target]}")
    for source, target in CONVERSION_PAIRS
] + [("binary_add", "Binary addition"), ("binary_subtract", "Binary subtraction")]


def base_string(number, base):
    if number == 0:
        return "0"
    result = ""
    while number:
        number, remainder = divmod(number, base)
        result = DIGITS[remainder] + result
    return result


def base_subscript(base):
    return str(base).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))


def table_data(headers, answer_rows, template_rows=None):
    """Store a table schema in the existing text fields without a DB migration."""
    answer = {"headers": headers, "rows": answer_rows}
    template = {"headers": headers, "rows": template_rows if template_rows is not None else answer_rows}
    return json.dumps(answer, ensure_ascii=False), json.dumps(template, ensure_ascii=False)


def decimal_division_table(number, base):
    answer_rows, template_rows = [], []
    value, accumulated = number, ""
    while value:
        quotient, remainder = divmod(value, base)
        digit = DIGITS[remainder]
        accumulated = digit + accumulated
        answer_rows.append([f"{value} / {base} = {quotient}", digit, accumulated])
        template_rows.append(["", "", ""])
        value = quotient
    return table_data(["Rechnung", "R", "GQ"], answer_rows, template_rows)


def positional_table(number, source):
    digits = base_string(number, source)
    answer_rows, template_rows = [], []
    for index, digit in enumerate(digits):
        power = len(digits) - index - 1
        value = int(digit, source) * source ** power
        answer_rows.append([digit, f"{source}^{power}", f"{int(digit, source)} × {source}^{power}", str(value)])
        template_rows.append([digit, f"{source}^{power}", "", ""])
    answer_rows.append(["", "", "Summe", str(number)])
    template_rows.append(["", "", "Summe", ""])
    return table_data(["Ziffer", "Stellenwert", "Rechnung", "Ergebnis"], answer_rows, template_rows)


def grouped_table(number, source, target):
    if source in (8, 16) and target == 2:
        width = 3 if source == 8 else 4
        digits = base_string(number, source)
        groups = [f"{int(d, source):0{width}b}" for d in digits]
        answers = [[digit, group] for digit, group in zip(digits, groups)]
        templates = [[digit, ""] for digit in digits]
        return table_data([f"Ziffer (Basis {source})", "Binärgruppe"], answers, templates)

    width = 3 if target == 8 else 4
    bits = base_string(number, 2)
    padded = bits.zfill(((len(bits) + width - 1) // width) * width)
    groups = [padded[i:i + width] for i in range(0, len(padded), width)]
    converted = [str(int(group, 2)) if target == 8 else DIGITS[int(group, 2)] for group in groups]
    answers = [[group, value] for group, value in zip(groups, converted)]
    templates = [[group, ""] for group in groups]
    answers.append(["Gesamtergebnis", base_string(number, target)])
    templates.append(["Gesamtergebnis", ""])
    return table_data([f"Binärgruppe ({width} Bit)", f"Ziffer (Basis {target})"], answers, templates)


def conversion_table(number, source, target):
    if source == 10:
        return decimal_division_table(number, target)
    if target == 10:
        return positional_table(number, source)

    first_answer, first_template = positional_table(number, source)
    second_answer, second_template = decimal_division_table(number, target)
    return (
        json.dumps({
            "tables": [
                {
                    "title": f"{BASE_NAMES[source]} → Decimal",
                    **json.loads(first_answer),
                },
                {
                    "title": f"Decimal → {BASE_NAMES[target]}",
                    **json.loads(second_answer),
                },
            ]
        }, ensure_ascii=False),
        json.dumps({
            "tables": [
                {
                    "title": f"{BASE_NAMES[source]} → Decimal",
                    **json.loads(first_template),
                },
                {
                    "title": f"Decimal → {BASE_NAMES[target]}",
                    **json.loads(second_template),
                },
            ]
        }, ensure_ascii=False),
    )


def _binary_layout_row(label, bits, width):
    """Align a bit string under the operand columns, including an overflow column."""
    bits = bits[-(width + 1):].rjust(width + 1)
    return [label, *[bit if bit.strip() else "" for bit in bits]]


def _binary_separator(width):
    return ["__SEPARATOR__", *[""] * (width + 1)]


def binary_arithmetic_table(a, b, operator):
    width = max(len(a), len(b))
    aa, bb = a.zfill(width), b.zfill(width)
    answer_rows, template_rows = [], []

    if operator == "+":
        carry = 0
        carry_outs = []
        result_reversed = []
        for left, right in zip(reversed(aa), reversed(bb)):
            total = int(left) + int(right) + carry
            result_reversed.append(str(total & 1))
            carry = total >> 1
            carry_outs.append(str(carry) if carry else "")

        result = (str(carry) if carry else "") + "".join(reversed(result_reversed))
        carry_row = [carry_outs[-1], *reversed(carry_outs[:-1]), ""] if carry_outs else [""] * (width + 1)

        answer_rows.extend([
            _binary_layout_row("", aa, width),
            _binary_layout_row("+", bb, width),
            _binary_separator(width),
            ["", *carry_row],
            _binary_separator(width),
            _binary_layout_row("Ergebnis", result, width),
        ])
        template_rows.extend([
            _binary_layout_row("", aa, width),
            _binary_layout_row("+", bb, width),
            _binary_separator(width),
            ["", *[""] * (width + 1)],
            _binary_separator(width),
            _binary_layout_row("Ergebnis", "", width),
        ])
    else:
        # Subtraction is shown using the two's-complement method:
        # invert B (B1), add one (B2), then add A + B2.
        mask = (1 << width) - 1
        b1 = "".join("1" if bit == "0" else "0" for bit in bb)
        b2_value = ((int(b1, 2) + 1) & mask)
        b2 = format(b2_value, f"0{width}b")

        carry = 0
        carry_outs = []
        result_reversed = []
        for left, right in zip(reversed(aa), reversed(b2)):
            total = int(left) + int(right) + carry
            result_reversed.append(str(total & 1))
            carry = total >> 1
            carry_outs.append(str(carry) if carry else "")

        # Two's-complement subtraction discards the final carry-out.
        final_sum = "".join(reversed(result_reversed))
        carry_row = [carry_outs[-1], *reversed(carry_outs[:-1]), ""] if carry_outs else [""] * (width + 1)
        one = "0" * (width - 1) + "1"

        answer_rows.extend([
            _binary_layout_row("", aa, width),
            _binary_layout_row("-", bb, width),
            _binary_separator(width),
            _binary_layout_row("B1", b1, width),
            _binary_layout_row("+", one, width),
            _binary_separator(width),
            _binary_layout_row("B2", b2, width),
            _binary_separator(width),
            _binary_layout_row("", aa, width),
            _binary_layout_row("+", b2, width),
            _binary_separator(width),
            ["", *carry_row],
            _binary_separator(width),
            _binary_layout_row("Ergebnis", final_sum, width),
        ])
        template_rows.extend([
            _binary_layout_row("", aa, width),
            _binary_layout_row("-", bb, width),
            _binary_separator(width),
            _binary_layout_row("B1", "", width),
            _binary_layout_row("+", one, width),
            _binary_separator(width),
            _binary_layout_row("B2", "", width),
            _binary_separator(width),
            _binary_layout_row("", aa, width),
            _binary_layout_row("+", "", width),
            _binary_separator(width),
            ["", *[""] * (width + 1)],
            _binary_separator(width),
            _binary_layout_row("Ergebnis", "", width),
        ])

    headers = ["__binary_layout__", *[""] * (width + 2)]
    return table_data(headers, answer_rows, template_rows)


class MathQuestionGenerator:
    """Creates and stores a fresh random Math question on demand."""
    def __init__(self, question_repository: QuestionRepository):
        self.questions = question_repository

    def generate_question_id(self, question_type="mix"):
        return self.questions.add_question(**self._generate(question_type))

    def _generate(self, question_type="mix"):
        available_types = [key for key, _label in MATH_QUESTION_TYPES]
        if question_type == "mix":
            question_type = random.choice(available_types)

        if question_type.startswith("convert_"):
            _, source, target = question_type.split("_")
            source, target = int(source), int(target)
            number = random.randint(12, 4095)
            source_value = base_string(number, source)
            answer, template = conversion_table(number, source, target)
            return {
                "subject_name": "Math",
                "topic_name": "Number Systems",
                "question_text": (
                    f"Convert {source_value}₍{base_subscript(source)}₎ from {BASE_NAMES[source]} "
                    f"to {BASE_NAMES[target]}."
                    + (" First convert to decimal, then to the target base. Complete both tables." if source != 10 and target != 10 else " Complete the table.")
                ),
                "answer": answer,
                "answer_template": template,
                "hint": "Complete each row, then read the final result in the target base.",
                "difficulty": 2 if source == 10 or target == 10 else 3,
            }

        if question_type not in {"binary_add", "binary_subtract"}:
            raise ValueError(f"Unknown math question type: {question_type}")

        width = random.randint(4, 8)
        first = random.randint(1 << (width - 1), (1 << width) - 1)
        second = random.randint(1 << (width - 2), (1 << (width - 1)) - 1)
        a, b = format(first, "b"), format(second, "b")
        operator = "+" if question_type == "binary_add" else "-"
        if operator == "-":
            a, b = (a, b) if first >= second else (b, a)
        answer, template = binary_arithmetic_table(a, b, operator)
        return {
            "subject_name": "Math",
            "topic_name": "Binary Arithmetic",
            "question_text": f"Calculate in binary: {a}₂ {operator} {b}₂. Complete the table.",
            "answer": answer,
            "answer_template": template,
            "hint": "Work from the rightmost bit to the left, one column at a time.",
            "difficulty": 2,
        }
