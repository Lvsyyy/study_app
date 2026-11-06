"""Generate fresh, bounded and internally consistent C# practice exercises.

This module generates one new exercise whenever an AE/OOP topic is opened.
It does not execute C#; code submissions are checked against the generated
reference solution, while output-reading tasks use the normal answer field.
"""
import itertools
import json
import random

from database.question_repository import QuestionRepository

NAMES = ("Alex", "Mia", "Noah", "Lena", "Max", "Emma", "Luca", "Nina")
COLORS = ("Rot", "Blau", "Gruen", "Gelb")


def _question(question_text, answer, hint=None, question_type="code"):
    return {
        "subject_name": "AE",
        "topic_name": None,
        "question_text": question_text,
        "answer": answer,
        "hint": hint,
        "difficulty": 1,
        "question_type": question_type,
    }


def _main(prompt, answer, hint=None, question_type="code"):
    """Build a question around a fixed, empty Main method shell."""
    shell = (
        f"{prompt.strip()}\n"
        "static void Main(string[] args)\n"
        "{\n"
        "    \n"
        "}"
    )
    return _question(shell, answer, hint, question_type)


def _practice_answer(solution, output, alternatives=()):
    """Serialise a practice task's reference solution and expected console output."""
    answer_data = {"solution": solution, "output": output}
    if alternatives:
        answer_data["alternatives"] = list(alternatives)
    return json.dumps(answer_data, ensure_ascii=False)


def _program(prompt, body, output, hint, alternatives=()):
    return _main(
        prompt, _practice_answer(body, output, alternatives), hint,
        question_type="csharp_practice",
    )


def _number_pair():
    a = random.randint(3, 30)
    b = random.randint(2, 12)
    return a, b


def _output():
    first, second = random.choice(
        (("Hallo Welt!", "Ich lerne C#."), ("Guten Morgen!", "C# macht Spaß."),
         ("Willkommen!", "Viel Erfolg beim Programmieren."))
    )
    body = (
        f'Console.WriteLine("{first}");\n'
        f'Console.WriteLine("{second}");\n'
        "Console.ReadLine();"
    )
    return _program(
        "Gib beide Texte jeweils in einer neuen Zeile aus.",
        body, first + "\n" + second,
        "Verwende für jede Zeile eine eigene Console.WriteLine-Anweisung."
    )


INPUT_FIELDS = (
    {
        "type": "string", "variables": ("name", "vorname"), "label": "Name",
        "values": NAMES,
        "prompts": ("Name: ", "Wie heißt du? ", "Gib deinen Namen ein: "),
    },
    {
        "type": "int", "variables": ("alter", "jahre"), "label": "Alter",
        "values": tuple(range(14, 26)),
        "prompts": ("Alter: ", "Wie alt bist du? ", "Gib dein Alter ein: "),
    },
    {
        "type": "string", "variables": ("wohnort", "stadt"), "label": "Wohnort",
        "values": ("Berlin", "München", "Hamburg", "Köln", "Dresden"),
        "prompts": ("Wohnort: ", "Wo wohnst du? ", "Gib deinen Wohnort ein: "),
    },
    {
        "type": "double", "variables": ("groesse", "koerpergroesse"), "label": "Größe",
        "values": (1.62, 1.68, 1.72, 1.75, 1.80, 1.84, 1.90),
        "prompts": ("Größe: ", "Wie groß bist du? ", "Gib deine Größe in Metern ein: "),
    },
    {
        "type": "int", "variables": ("geschwister", "anzahlGeschwister"), "label": "Geschwister",
        "values": (0, 1, 2, 3, 4),
        "prompts": ("Geschwister: ", "Wie viele Geschwister hast du? ",
                    "Gib die Anzahl deiner Geschwister ein: "),
    },
    {
        "type": "string", "variables": ("lieblingsfarbe", "farbe"), "label": "Lieblingsfarbe",
        "values": COLORS,
        "prompts": ("Lieblingsfarbe: ", "Was ist deine Lieblingsfarbe? ",
                    "Gib deine Lieblingsfarbe ein: "),
    },
    {
        "type": "double", "variables": ("gewicht", "koerpergewicht"), "label": "Gewicht",
        "values": (48.5, 55.0, 62.5, 70.0, 74.5, 81.0, 92.5),
        "prompts": ("Gewicht: ", "Wie viel wiegst du in kg? ",
                    "Gib dein Gewicht in kg ein: "),
    },
)


def _input_conversion(field, method):
    if field["type"] == "string":
        return f'string {field["variable"]} = Console.ReadLine();'
    return (
        f'{field["type"]} {field["variable"]} = '
        f'{method}(Console.ReadLine());'
    )


def _input_solution(fields, conversions, output_style, output_layout):
    lines = []
    for index, (field, conversion) in enumerate(zip(fields, conversions, strict=True)):
        prompt = field["prompt"].replace("\\", "\\\\").replace('"', '\\"')
        # Explicitly separate successive prompts in the generated console stream.
        # The preview includes the entered values, so the code must emit the
        # same line break before asking for the next value.
        prefix = "\\n" if index else ""
        lines.extend((
            f'Console.Write("{prefix}{prompt}");',
            _input_conversion(field, conversion),
        ))

    if output_layout == "combined":
        labels = "\\n".join(
            f'{field["label"]}: {{{index}}}'
            for index, field in enumerate(fields)
        )
        values = ", ".join(field["variable"] for field in fields)
        if output_style == "interpolation":
            interpolated = "\\n".join(
                f'{field["label"]}: {{{field["variable"]}}}'
                for field in fields
            )
            lines.append(f'Console.WriteLine($"\\n{interpolated}");')
        else:
            lines.append(f'Console.WriteLine("\\n{labels}", {values});')
    else:
        for index, field in enumerate(fields):
            prefix = "\\n" if index == 0 else ""
            if output_style == "interpolation":
                lines.append(
                    f'Console.WriteLine($"\\n{field["label"]}: '
                    f'{{{field["variable"]}}}");'
                    if index == 0 else
                    f'Console.WriteLine($"{field["label"]}: '
                    f'{{{field["variable"]}}}");'
                )
            else:
                lines.append(
                    f'Console.WriteLine("{prefix}{field["label"]}: '
                    f'{{0}}", {field["variable"]});'
                )

    lines.append("Console.ReadLine();")
    return "\n".join(lines)


def _input():
    fields = [
        dict(field)
        for field in random.sample(INPUT_FIELDS, random.randint(1, 3))
    ]
    for field in fields:
        field["variable"] = random.choice(field["variables"])
        field["prompt"] = random.choice(field["prompts"])
        field["value"] = random.choice(field["values"])

    question_lines = [
        "Frage den Benutzer nach den folgenden Angaben und gib alle "
        "eingegebenen Werte anschließend aus:"
    ]
    question_lines.extend(
        f'- {field["label"]} – verwende die Variable '
        f'{field["type"]} {field["variable"]}.'
        for field in fields
    )
    question = "\n".join(question_lines)

    input_output = "\n".join(
        f'{field["prompt"]}{_input_display_value(field)}'
        for field in fields
    )

    conversion_options = [
        ("Convert.ToInt32", "Int32.Parse") if field["type"] == "int" else
        ("Convert.ToDouble", "Double.Parse") if field["type"] == "double" else
        (None,)
        for field in fields
    ]
    output_options = tuple(itertools.product(
        ("interpolation", "format"),
        ("combined", "separate"),
    ))
    accepted = []
    for conversions in itertools.product(*conversion_options):
        for output_style, output_layout in output_options:
            accepted.append(_input_solution(
                fields, conversions, output_style, output_layout
            ))

    selected_style, selected_layout = random.choice(output_options)
    selected_conversions = tuple(
        random.choice(options) for options in conversion_options
    )
    solution = _input_solution(
        fields, selected_conversions, selected_style, selected_layout
    )
    alternatives = [candidate for candidate in accepted if candidate != solution]

    result_lines = [
        f'{field["label"]}: {_input_display_value(field)}'
        for field in fields
    ]
    result_output = "\n".join(result_lines)
    expected_output = f"{input_output}\n\n{result_output}"
    hints = (
        "Verwende Console.Write() für die Eingabeaufforderungen, "
        "Console.ReadLine() zum Einlesen und die angegebenen Datentypen. "
        "Für int und double sind die beiden üblichen Konvertierungen erlaubt."
    )
    return _program(
        question,
        solution, expected_output, hints, alternatives=alternatives,
    )


def _input_display_value(field):
    value = field["value"]
    if field["type"] == "double":
        return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    return str(value)


def _variables():
    name = random.choice(NAMES)
    age = random.randint(14, 25)
    height = random.choice((1.62, 1.68, 1.72, 1.75, 1.80, 1.84, 1.90))
    height_text = str(height).replace(".", ",").rstrip("0").rstrip(",")
    style = random.choice(("interpolation", "format"))
    declarations = (
        f'string name = "{name}";\n'
        f"int alter = {age};\n"
        f"double groesse = {height:.2f};"
    )
    if style == "interpolation":
        output_lines = [
            f'Console.WriteLine($"{{{variable}}}");'
            for variable in ("name", "alter", "groesse")
        ]
    else:
        output_lines = [
            f'Console.WriteLine("{{0}}", {variable});'
            for variable in ("name", "alter", "groesse")
        ]
    body = "\n".join((declarations, *output_lines, "Console.ReadLine();"))
    return _program(
        "Erstelle die Variablen name, alter und groesse mit den vorgegebenen Werten "
        "und gib sie jeweils in einer neuen Zeile aus.",
        body, f"{name}\n{age}\n{height_text}",
        "Verwende string, int und double für die drei Datentypen."
    )


def _formatting():
    first = random.choice(NAMES)
    last = random.choice(("Mustermann", "Schmidt", "Fischer", "Weber"))
    age = random.randint(15, 25)
    style = random.choice(("interpolation", "format"))
    declarations = (
        f'string vorname = "{first}";\n'
        f'string nachname = "{last}";\n'
        f"int alter = {age};"
    )
    if style == "interpolation":
        output_line = (
            'Console.WriteLine($"Name:\\t{vorname} {nachname}\\n'
            'Alter:\\t{alter}");'
        )
    else:
        output_line = (
            'Console.WriteLine("Name:\\t{0} {1}\\nAlter:\\t{2}", '
            'vorname, nachname, alter);'
        )
    body = "\n".join((declarations, output_line, "Console.ReadLine();"))
    output = f"Name:\t{first} {last}\nAlter:\t{age}"
    return _program(
        "Erstelle vorname, nachname und alter. Formatiere die Ausgabe mit \\t und "
        "\\n. Verwende dafür genau eine Console.WriteLine-Anweisung.",
        body, output,
        "\\t erzeugt einen Tabulator, \\n einen Zeilenumbruch. Nur eine WriteLine verwenden."
    )


def _operators():
    a, b = _number_pair()
    style = random.choice(("interpolation", "format"))
    # The comparison variant accepts either output style; the variable variant
    # only accepts the style it was generated with.
    accepts_both_styles = True
    if random.choice((True, False)):
        accepts_both_styles = False
        total, difference, product = a + b, a - b, a * b
        declarations = (
            f"int zahl1 = {a};\nint zahl2 = {b};\n"
            "int summe = zahl1 + zahl2;\n"
            "int differenz = zahl1 - zahl2;\n"
            "int produkt = zahl1 * zahl2;"
        )
        labels = (("Zahl1", "zahl1"), ("Zahl2", "zahl2"),
                  ("Summe", "summe"), ("Differenz", "differenz"),
                  ("Produkt", "produkt"))
        output = (
            f"Zahl1 = {a}\nZahl2 = {b}\nSumme = {total}\n"
            f"Differenz = {difference}\nProdukt = {product}"
        )
        prompt = (
            "Erstelle zahl1 und zahl2. Berechne Summe, Differenz und Produkt in "
            "eigenen Variablen und gib alle fünf Werte mit Beschriftung aus."
        )
        def build(selected):
            lines = [declarations]
            for label, variable in labels:
                if selected == "interpolation":
                    lines.append(f'Console.WriteLine($"{label} = {{{variable}}}");')
                else:
                    lines.append(f'Console.WriteLine("{label} = {{0}}", {variable});')
            lines.append("Console.ReadLine();")
            return "\n".join(lines)
    else:
        expressions = (
            (f"{a} == {b}", "zahl1 == zahl2", a == b),
            (f"{a} != {b}", "zahl1 != zahl2", a != b),
            (f"{a} > {b}", "zahl1 > zahl2", a > b),
            (f"{a} < {b}", "zahl1 < zahl2", a < b),
        )
        output = "\n".join(f"{label}: {str(result)}" for label, _, result in expressions)
        prompt = (
            "Erstelle zahl1 und zahl2. Vergleiche sie mit ==, !=, > und <. "
            "Gib jeweils den Vergleich und sein Ergebnis aus."
        )
        declarations = f"int zahl1 = {a};\nint zahl2 = {b};"
        def build(selected):
            lines = [declarations]
            for label, expression, _ in expressions:
                if selected == "interpolation":
                    lines.append(f'Console.WriteLine($"{label}: {{{expression}}}");')
                else:
                    lines.append(f'Console.WriteLine("{label}: {{0}}", ({expression}));')
            lines.append("Console.ReadLine();")
            return "\n".join(lines)
    solution = build(style)
    alternatives = (
        [build(other) for other in ("interpolation", "format") if other != style]
        if accepts_both_styles else []
    )
    return _program(
        prompt, solution, output,
        "Verwende String-Interpolation ($\"... {variable}\") oder den "
        "Console.WriteLine-Formatparameter ({0}). Keine String-Verkettung.",
        alternatives=alternatives,
    )


def _if_condition():
    age = random.randint(18, 30)
    prompt = (
        f"Ergänze nur die Bedingung. Bei einem Alter ab 18 soll 'Volljaehrig' "
        f"ausgegeben werden. Variable: alter = {age}.\n"
        "static void Main(string[] args)\n{\n"
        f"    int alter = {age};\n"
        "    if (________________)\n    {\n"
        '        Console.WriteLine("Volljaehrig");\n    }\n'
        "    Console.ReadLine();\n}"
    )
    return _question(
        prompt,
        _practice_answer("alter >= 18", "Volljaehrig" if age >= 18 else ""),
        "Vergleiche alter mit 18.",
        question_type="csharp_practice",
    )


def _if_output():
    points = random.choice((50, 63, 75, 88, 100))
    body = (
        f"int punkte = {points};\n"
        "if (punkte >= 50)\n{\n"
        '    Console.WriteLine("Bestanden");\n'
        "}\n"
        "Console.ReadLine();"
    )
    return _program(
        "Schreibe eine if-Anweisung, die bei mindestens 50 Punkten "
        "'Bestanden' ausgibt.\n"
        f"Variable: punkte = {points}\n"
        "Erwartete Konsolenausgabe: Bestanden",
        body, "Bestanden",
        "Die Bedingung soll prüfen, ob punkte mindestens 50 ist."
    )


def _if_else_condition():
    temperature = random.randint(5, 35)
    prompt = (
        "Ergänze nur die Bedingung. Bei mindestens 20 Grad soll 'Warm', "
        f"andernfalls 'Kalt' ausgegeben werden. temperatur = {temperature}.\n"
        "static void Main(string[] args)\n{\n"
        f"    int temperatur = {temperature};\n"
        "    if (________________)\n    {\n"
        '        Console.WriteLine("Warm");\n    }\n    else\n    {\n'
        '        Console.WriteLine("Kalt");\n    }\n'
        "    Console.ReadLine();\n}"
    )
    return _question(
        prompt,
        _practice_answer("temperatur >= 20", "Warm" if temperature >= 20 else "Kalt"),
        "Vergleiche temperatur mit 20.",
        question_type="csharp_practice",
    )


def _if_else_output():
    age = random.randint(14, 25)
    output = "Volljährig" if age >= 18 else "Minderjährig"
    body = (
        f"int alter = {age};\n"
        "if (alter >= 18)\n{\n"
        '    Console.WriteLine("Volljährig");\n'
        "}\nelse\n{\n"
        '    Console.WriteLine("Minderjährig");\n'
        "}\nConsole.ReadLine();"
    )
    return _program(
        "Schreibe eine if-else-Anweisung, die prüft, ob eine Person "
        "volljährig ist.\n"
        f"Variable: alter = {age}\n"
        f"Erwartete Konsolenausgabe: {output}",
        body, output,
        "Prüfe mit alter >= 18. Für den anderen Fall wird else verwendet."
    )



# Each practice topic picks one of its generator variants at random.
TOPIC_VARIANTS = {
    "Ausgabe": (_output,),
    "Eingabe": (_input,),
    "Variablen": (_variables,),
    "Ausgabe formatierung": (_formatting,),
    "Operatoren": (_operators,),
    "Bedingungen": (_if_condition, _if_output),
    "Verzweigte Bedingungen": (_if_else_condition, _if_else_output),
}


class CSharpQuestionGenerator:
    """Creates unlimited parameterized exercises for the existing AE/OOP topics."""

    def __init__(self, repository: QuestionRepository):
        self.repository = repository

    def generate_question_id(self, topic_name):
        variants = TOPIC_VARIANTS.get(topic_name)
        if variants is None:
            raise ValueError(f"Unknown practice topic: {topic_name}")
        question = random.choice(variants)()
        question["topic_name"] = topic_name
        return self.repository.add_question(**question)
