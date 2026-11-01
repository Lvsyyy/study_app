"""Generate fresh worked math questions on demand."""
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


def decimal_to_base(number, base):
    lines, value = [], number
    while value:
        quotient, remainder = divmod(value, base)
        lines.append(f"{value} / {base} = {quotient} R {DIGITS[remainder]}")
        value = quotient
    lines.append(f"Read remainders bottom to top: {base_string(number, base)}")
    return "\n".join(lines)


def positional_expansion(number, base):
    digits = base_string(number, base)
    terms = [f"{int(d, base)}*{base}^{len(digits)-i-1}" for i, d in enumerate(digits)]
    values = [int(d, base) * base ** (len(digits)-i-1) for i, d in enumerate(digits)]
    return f"{digits} = " + " + ".join(terms) + "\n" + " = ".join([" + ".join(map(str, values)), str(number)])


def grouped_conversion(number, source, target):
    bits = base_string(number, 2)
    if source in (8, 16) and target == 2:
        width = 3 if source == 8 else 4
        digits = base_string(number, source)
        groups = [f"{int(d, source):0{width}b}" for d in digits]
        result = "".join(groups).lstrip("0") or "0"
        return (f"Convert each {BASE_NAMES[source]} digit to {width} bits:\n"
                f"{' '.join(digits)} -> {' | '.join(groups)}\n"
                f"Join the groups and remove leading zeroes: {result}")
    width = 3 if target == 8 else 4
    padded = bits.zfill(((len(bits) + width - 1) // width) * width)
    groups = [padded[i:i+width] for i in range(0, len(padded), width)]
    converted = " ".join(str(int(g, 2)) if target == 8 else DIGITS[int(g, 2)] for g in groups)
    if source == 2:
        return (f"Group into {width}-bit chunks from the right:\n{padded} -> {' | '.join(groups)}\n"
                f"Convert each group: {converted}\nResult: {base_string(number, target)}")
    source_width = 3 if source == 8 else 4
    source_digits = base_string(number, source)
    source_groups = [f"{int(d, source):0{source_width}b}" for d in source_digits]
    return (f"Convert each base-{source} digit to {source_width} bits:\n"
            f"{' '.join(source_digits)} -> {' | '.join(source_groups)}\n"
            f"Group into {width}-bit chunks from the right:\n{padded} -> {' | '.join(groups)}\n"
            f"Convert each group: {converted}\nResult: {base_string(number, target)}")


def conversion_work(number, source, target):
    if source == 10:
        return decimal_to_base(number, target)
    if target == 10:
        return positional_expansion(number, source)
    return grouped_conversion(number, source, target)


def conversion_template(number, source, target):
    source_value = base_string(number, source)
    if source == 10:
        lines, value = [], number
        while value:
            lines.append(f"{value} / {target} = ____ R ____")
            value //= target
        lines.append("Read remainders bottom to top: ______")
        return "\n".join(lines)
    if target == 10:
        terms = [f"{int(d, source)}*{source}^{len(source_value)-i-1}" for i, d in enumerate(source_value)]
        return f"{source_value} = " + " + ".join(terms) + "\n= ____________________\n= ______"
    if source in (8, 16) and target == 2:
        width = 3 if source == 8 else 4
        return (f"Convert each base-{source} digit to {width} bits:\n"
                f"{' '.join(source_value)} -> {' | '.join('___' for _ in source_value)}\n"
                "Join the groups and remove leading zeroes: ______")
    width = 3 if target == 8 else 4
    bits = base_string(number, 2)
    padded = bits.zfill(((len(bits)+width-1)//width)*width)
    groups = [padded[i:i+width] for i in range(0, len(padded), width)]
    if source == 2:
        return (f"Group into {width}-bit chunks from the right:\n"
                f"{padded} -> {' | '.join('____' for _ in groups)}\n"
                "Convert each group: ____________________\nResult: ______")
    source_width = 3 if source == 8 else 4
    return (f"Convert each base-{source} digit to {source_width} bits:\n"
            f"{' '.join(source_value)} -> {' | '.join('___' for _ in source_value)}\n"
            "Join the binary groups: ____________________\n"
            f"Group into {width}-bit chunks:\n{' | '.join('____' for _ in groups)}\n"
            f"Convert groups to base {target}: ______")


def add_binary(a, b):
    width = max(len(a), len(b))
    aa, bb = a.zfill(width), b.zfill(width)
    carry, carries, result = 0, [], []
    for left, right in zip(reversed(aa), reversed(bb)):
        total = int(left) + int(right) + carry
        result.append(str(total % 2))
        carry = total // 2
        carries.append(str(carry))
    if carry:
        result.append("1")
    result = "".join(reversed(result))
    return (f"  {aa}\n+ {bb}\n{'-'*(width+2)}\n  {result}\n"
            f"Carry values (right to left): {''.join(carries)}\n"
            f"Check: {int(aa,2)} + {int(bb,2)} = {int(aa,2)+int(bb,2)}")


def subtract_binary(a, b):
    width = max(len(a), len(b))
    aa, bb = a.zfill(width), b.zfill(width)
    if int(aa, 2) < int(bb, 2):
        aa, bb = bb, aa
    borrow, borrows, result = 0, [], []
    for left, right in zip(reversed(aa), reversed(bb)):
        value = int(left) - int(right) - borrow
        borrow = int(value < 0)
        result.append(str(value + 2 if borrow else value))
        borrows.append(str(borrow))
    result = "".join(reversed(result))
    return (f"  {aa}\n- {bb}\n{'-'*(width+2)}\n  {result}\n"
            f"Borrow values (right to left): {''.join(borrows)}\n"
            f"Check: {int(aa,2)} - {int(bb,2)} = {int(result,2)}")


def arithmetic_template(a, b, operator):
    width = max(len(a), len(b))
    aa, bb = a.zfill(width), b.zfill(width)
    sign = "+" if operator == "+" else "-"
    detail = "Carry values (right to left)" if operator == "+" else "Borrow values (right to left)"
    return (f"  {aa}\n{sign} {bb}\n{'-'*(width+2)}\n  ______\n"
            f"{detail}: ____\nCheck: ____________________")


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
            return {
                "subject_name": "Math",
                "topic_name": "Number Systems",
                "question_text": (f"Convert {source_value}₍{source}₎ from {BASE_NAMES[source]} "
                                  f"to {BASE_NAMES[target]}. Show every calculation step."),
                "answer": conversion_work(number, source, target),
                "answer_template": conversion_template(number, source, target),
                "hint": "Keep each base clear and show the complete conversion path.",
                "difficulty": 2 if source == 10 or target == 10 else 3,
            }

        width = random.randint(4, 8)
        first = random.randint(1 << (width-1), (1 << width)-1)
        second = random.randint(1 << (width-2), (1 << (width-1))-1)
        a, b = format(first, "b"), format(second, "b")
        operator = "+" if kind == len(CONVERSION_PAIRS) else "-"
        if operator == "-":
            a, b = (a, b) if first >= second else (b, a)
            answer = subtract_binary(a, b)
        else:
            answer = add_binary(a, b)
        return {
            "subject_name": "Math",
            "topic_name": "Binary Arithmetic",
            "question_text": f"Calculate in binary: {a}₂ {operator} {b}₂. Align the numbers and show all carries or borrows.",
            "answer": answer,
            "answer_template": arithmetic_template(a, b, operator),
            "hint": "Work one column at a time from right to left.",
            "difficulty": 2,
        }
