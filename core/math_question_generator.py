"""Generate fresh, table-based math questions on demand."""
import json
import random

from database.question_repository import QuestionRepository

DIGITS = "0123456789ABCDEF"
BASE_NAMES = {2: "Binary", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}
CONVERSION_PAIRS = [(s, t) for s in (2, 8, 10, 16) for t in (2, 8, 10, 16) if s != t]


def base_string(number, base):
    if number == 0:
        return "0"
    result = ""
    while number:
        number, remainder = divmod(number, base)
        result = DIGITS[remainder] + result
    return result


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
    return grouped_table(number, source, target)


def binary_arithmetic_table(a, b, operator):
    width = max(len(a), len(b))
    aa, bb = a.zfill(width), b.zfill(width)
    carry_or_borrow = 0
    answer_rows, template_rows = [], []

    for index, (left, right) in enumerate(zip(reversed(aa), reversed(bb))):
        if operator == "+":
            total = int(left) + int(right) + carry_or_borrow
            result_bit = str(total % 2)
            next_value = total // 2
            detail = str(carry_or_borrow)
        else:
            raw = int(left) - int(right) - carry_or_borrow
            next_value = int(raw < 0)
            result_bit = str(raw + 2 if next_value else raw)
            detail = str(carry_or_borrow)
        answer_rows.append([f"2^{index}", left, right, detail, result_bit])
        template_rows.append([f"2^{index}", left, right, "", ""])
        carry_or_borrow = next_value

    if operator == "+" and carry_or_borrow:
        answer_rows.append(["Übertrag", "", "", str(carry_or_borrow), str(carry_or_borrow)])
        template_rows.append(["Übertrag", "", "", "", ""])
    result = "".join(row[4] for row in reversed(answer_rows) if row[0] != "Übertrag")
    if operator == "+" and carry_or_borrow:
        result = "1" + result
    answer_rows.append(["Ergebnis", "", "", "", result])
    template_rows.append(["Ergebnis", "", "", "", ""])
    return table_data(
        ["Stelle", "A", "B", "Übertrag" if operator == "+" else "Entleihen", "Ergebnis"],
        answer_rows,
        template_rows,
    )


class MathQuestionGenerator:
    """Creates and stores a fresh random Math question on demand."""
    def __init__(self, question_repository: QuestionRepository):
        self.questions = question_repository

    def generate_question_id(self):
        return self.questions.add_question(**self._generate())

    def _generate(self):
        kind = random.randrange(len(CONVERSION_PAIRS) + 2)
        if kind < len(CONVERSION_PAIRS):
            source, target = CONVERSION_PAIRS[kind]
            number = random.randint(12, 4095)
            source_value = base_string(number, source)
            answer, template = conversion_table(number, source, target)
            return {
                "subject_name": "Math",
                "topic_name": "Number Systems",
                "question_text": (f"Convert {source_value}₍{source}₎ from {BASE_NAMES[source]} "
                                  f"to {BASE_NAMES[target]}. Complete the table."),
                "answer": answer,
                "answer_template": template,
                "hint": "Complete each row, then read the final result in the target base.",
                "difficulty": 2 if source == 10 or target == 10 else 3,
            }

        width = random.randint(4, 8)
        first = random.randint(1 << (width - 1), (1 << width) - 1)
        second = random.randint(1 << (width - 2), (1 << (width - 1)) - 1)
        a, b = format(first, "b"), format(second, "b")
        operator = "+" if kind == len(CONVERSION_PAIRS) else "-"
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
