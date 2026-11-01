"""Seed worked number-system and binary arithmetic practice questions.

Run from the project root:
    python dev_math_questions.py

Safe to run repeatedly: existing generated questions are not duplicated.
"""

from database.database import Database
from database.question_repository import QuestionRepository


DIGITS = "0123456789ABCDEF"


def base_string(number, base):
    if number == 0:
        return "0"
    result = ""
    while number:
        number, remainder = divmod(number, base)
        result = DIGITS[remainder] + result
    return result


def grouped_binary(number, width):
    bits = base_string(number, 2)
    bits = bits.zfill(((len(bits) + width - 1) // width) * width)
    return " ".join(bits[i:i + width] for i in range(0, len(bits), width))


def decimal_to_base(number, base):
    lines = []
    value = number
    while value:
        quotient, remainder = divmod(value, base)
        lines.append(f"{value} / {base} = {quotient} R {remainder}")
        value = quotient
    lines.append(f"Read remainders bottom to top: {base_string(number, base)}")
    return "\n".join(lines)


def positional_expansion(number, base):
    digits = base_string(number, base)
    terms = [
        f"{DIGITS.index(digit)}*{base}^{len(digits) - index - 1}"
        for index, digit in enumerate(digits)
    ]
    values = [
        DIGITS.index(digit) * (base ** (len(digits) - index - 1))
        for index, digit in enumerate(digits)
    ]
    return (
        f"{digits} = " + " + ".join(terms) + "\n"
        + " = ".join([" + ".join(map(str, values)), str(number)])
    )


def binary_group_conversion(number, source, target):
    if source == 2 and target == 8:
        width, label = 3, "Groups of 3 bits"
    elif source == 2 and target == 16:
        width, label = 4, "Groups of 4 bits"
    elif source == 8 and target == 2:
        digits = base_string(number, 8)
        converted = " ".join(f"{int(digit):03b}" for digit in digits)
        return f"Convert each octal digit to 3 bits:\n{digits} -> {converted}\nRemove leading zeroes: {base_string(number, 2)}"
    elif source == 16 and target == 2:
        digits = base_string(number, 16)
        converted = " ".join(f"{int(digit, 16):04b}" for digit in digits)
        return f"Convert each hexadecimal digit to 4 bits:\n{digits} -> {converted}\nRemove leading zeroes: {base_string(number, 2)}"
    else:
        bits = base_string(number, 2)
        width = 3 if target == 8 else 4
        label = f"Group into {width}-bit chunks from the right"
        padded = bits.zfill(((len(bits) + width - 1) // width) * width)
        groups = [padded[i:i + width] for i in range(0, len(padded), width)]
        converted = " ".join(str(int(group, 2)) if target == 8 else DIGITS[int(group, 2)] for group in groups)
        source_digits = base_string(number, source)
        source_width = 3 if source == 8 else 4
        source_bits = " ".join(f"{int(digit, source):0{source_width}b}" for digit in source_digits)
        return (
            f"Convert each base-{source} digit to {source_width} bits: "
            f"{source_digits} -> {source_bits}\n"
            f"{label}:\n{padded} -> {' | '.join(groups)}\n"
            f"Convert each group: {converted}\nResult: {base_string(number, target)}"
        )
    bits = base_string(number, 2)
    padded = bits.zfill(((len(bits) + width - 1) // width) * width)
    groups = [padded[i:i + width] for i in range(0, len(padded), width)]
    converted = " ".join(str(int(group, 2)) if target == 8 else DIGITS[int(group, 2)] for group in groups)
    return f"{label}:\n{padded} -> {' | '.join(groups)}\nConvert each group: {converted}\nResult: {base_string(number, target)}"


def conversion_work(number, source, target):
    source_value = base_string(number, source)
    target_value = base_string(number, target)
    if source == 10:
        return decimal_to_base(number, target)
    if target == 10:
        return positional_expansion(number, source)
    if source in (2, 8, 16) and target in (2, 8, 16):
        return binary_group_conversion(number, source, target)
    raise ValueError((source, target))


def conversion_template(number, source, target):
    source_value = base_string(number, source)
    if source == 10:
        lines = []
        value = number
        while value:
            lines.append(f"{value} / {target} = ____ R ____")
            value //= target
        lines.append("Read remainders bottom to top: ______")
        return "\n".join(lines)
    if target == 10:
        digits = source_value
        terms = [
            f"{DIGITS.index(digit)}*{source}^{len(digits) - index - 1}"
            for index, digit in enumerate(digits)
        ]
        return f"{digits} = " + " + ".join(terms) + "\n= ____________________\n= ______"
    width = 3 if target == 8 else 4
    if source == 2:
        bits = source_value.zfill(((len(source_value) + width - 1) // width) * width)
        groups = [bits[i:i + width] for i in range(0, len(bits), width)]
        return (
            f"Group into {width}-bit chunks:\n"
            f"{bits} -> {' | '.join('____' for _ in groups)}\n"
            f"Convert groups: ____________________\nResult: ______"
        )
    if source in (8, 16) and target == 2:
        digits = source_value
        width = 3 if source == 8 else 4
        return (
            f"Convert each base-{source} digit to {width} bits:\n"
            f"{' '.join(digits)} -> {' | '.join('___' for _ in digits)}\n"
            "Join the groups: ____________________\nRemove leading zeroes: ______"
        )
    # Octal <-> hexadecimal: convert through binary.
    bits = base_string(number, 2)
    first_width = 3 if source == 8 else 4
    second_width = 3 if target == 8 else 4
    first_groups = (len(bits) + first_width - 1) // first_width
    second_groups = (len(bits) + second_width - 1) // second_width
    return (
        f"Convert {source_value} from base {source} to binary:\n"
        f"Binary groups: {' | '.join('___' for _ in range(first_groups))}\n"
        f"Binary number: ____________________\n"
        f"Group binary into {second_width}-bit chunks:\n"
        f"{' | '.join('____' for _ in range(second_groups))}\n"
        f"Convert groups to base {target}: ______"
    )


def add_binary(a, b):
    width = max(len(a), len(b))
    aa, bb = a.zfill(width), b.zfill(width)
    carry = 0
    carries = []
    result = []
    for left, right in zip(reversed(aa), reversed(bb)):
        total = int(left) + int(right) + carry
        result.append(str(total % 2))
        carry = total // 2
        carries.append(str(carry))
    if carry:
        result.append("1")
    result = "".join(reversed(result))
    carry_row = "".join(carries)
    decimal_total = int(aa, 2) + int(bb, 2)
    return (
        f"  {aa}\n+ {bb}\n{'-' * (width + 2)}\n  {result}\n"
        f"Carry values (right to left): {carry_row}\n"
        f"Check: {int(aa, 2)} + {int(bb, 2)} = {decimal_total}"
    )


def subtract_binary(a, b):
    width = max(len(a), len(b))
    aa, bb = a.zfill(width), b.zfill(width)
    if int(aa, 2) < int(bb, 2):
        aa, bb = bb, aa
    borrow = 0
    borrows = []
    result = []
    for left, right in zip(reversed(aa), reversed(bb)):
        value = int(left) - int(right) - borrow
        next_borrow = int(value < 0)
        result.append(str(value + 2 if next_borrow else value))
        borrow = next_borrow
        borrows.append(str(borrow))
    result = "".join(reversed(result))
    borrow_row = "".join(borrows)
    return (
        f"  {aa}\n- {bb}\n{'-' * (width + 2)}\n  {result}\n"
        f"Borrow values (right to left): {borrow_row}\n"
        f"Check: {int(aa, 2)} - {int(bb, 2)} = {int(result, 2)}"
    )


def arithmetic_template(a, b, operator):
    width = max(len(a), len(b))
    aa, bb = a.zfill(width), b.zfill(width)
    sign = "+" if operator == "+" else "-"
    detail = "Carry values (right to left)" if operator == "+" else "Borrow values (right to left)"
    return (
        f"  {aa}\n{sign} {bb}\n{'-' * (width + 2)}\n  ______\n"
        f"{detail}: ____\nCheck: ____________________"
    )


def build_questions():
    questions = []
    bases = {2: "Dual (Binary)", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}
    # Every ordered conversion pair, with two different values.
    values = (173, 58)
    for source in (2, 8, 10, 16):
        for target in (2, 8, 10, 16):
            if source == target:
                continue
            for number in values:
                source_value = base_string(number, source)
                target_value = base_string(number, target)
                questions.append({
                    "subject_name": "Math",
                    "topic_name": "Number Systems",
                    "question_text": (
                        f"Convert {source_value}₍{source}₎ from {bases[source]} "
                        f"to {bases[target]}. Show every calculation step."
                    ),
                    "answer": conversion_work(number, source, target),
                    "answer_template": conversion_template(number, source, target),
                    "hint": "Keep the base of every number clear. Show the full conversion path.",
                    "difficulty": 2 if source == 10 or target == 10 else 3,
                })

    operations = [
        ("1011", "0110", "+"),
        ("1101", "0101", "+"),
        ("11010", "00111", "-"),
        ("10101", "01011", "-"),
    ]
    for a, b, operator in operations:
        answer = add_binary(a, b) if operator == "+" else subtract_binary(a, b)
        questions.append({
            "subject_name": "Math",
            "topic_name": "Binary Arithmetic",
            "question_text": (
                f"Calculate in binary: {a}₂ {operator} {b}₂. "
                "Align the numbers and show all carries or borrows."
            ),
            "answer": answer,
            "answer_template": arithmetic_template(a, b, operator),
            "hint": "Work one column at a time from right to left.",
            "difficulty": 2,
        })
    return questions


def main():
    db = Database()
    try:
        repo = QuestionRepository(db)
        questions = build_questions()
        subjects = {row["name"] for row in repo.list_subjects()}
        if any(q["subject_name"] not in subjects for q in questions):
            raise RuntimeError("The Math subject does not exist in this database.")

        pending = []
        for question in questions:
            exists = db.fetch_one(
                """SELECT 1
                   FROM questions q
                   JOIN topics t ON t.id = q.topic_id
                   JOIN subjects s ON s.id = t.subject_id
                   WHERE s.name = ? AND t.name = ? AND q.question_text = ?
                   LIMIT 1""",
                (question["subject_name"], question["topic_name"], question["question_text"]),
            )
            if not exists:
                pending.append(question)

        if pending:
            repo.add_questions(pending)
        print(f"Inserted {len(pending)} questions; skipped {len(questions) - len(pending)} existing questions.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
