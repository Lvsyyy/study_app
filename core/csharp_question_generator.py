"""Generate fresh, bounded and internally consistent C# practice exercises.

This module generates one new exercise whenever an AE/OOP topic is opened.
It does not execute C#; code submissions are checked against the generated
reference solution, while output-reading tasks use the normal answer field.
"""
import json
import itertools
import random

from database.question_repository import QuestionRepository


NAMES = ("Alex", "Mia", "Noah", "Lena", "Max", "Emma", "Luca", "Nina")
COLORS = ("Rot", "Blau", "Gruen", "Gelb")
ITEMS = ("Apfel", "Birne", "Buch", "Stift", "Tasche", "Ball")


def _main(prompt, body, answer, hint=None, question_type="code"):
    shell = (
        f"{prompt.strip()}\n"
        "static void Main(string[] args)\n"
        "{\n"
        "    \n"
        "}"
    )
    return {
        "subject_name": "AE",
        "topic_name": None,
        "question_text": shell,
        "answer": answer,
        "hint": hint,
        "difficulty": 1,
        "question_type": question_type,
    }


def _program(prompt, body, output, hint, alternatives=()):
    answer_data = {"solution": body, "output": output}
    if alternatives:
        answer_data["alternatives"] = list(alternatives)
    return _main(
        prompt, body,
        __import__("json").dumps(answer_data, ensure_ascii=False),
        hint, question_type="csharp_practice",
    )


def _number_pair():
    a = random.randint(3, 30)
    b = random.randint(2, 12)
    return a, b


def _output():
    first, second = random.sample(
        (("Hallo Welt!", "Ich lerne C#."), ("Guten Morgen!", "C# macht Spaß."),
         ("Willkommen!", "Viel Erfolg beim Programmieren.")), 1
    )[0]
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
        "type": "string", "variable": "name", "label": "Name",
        "values": NAMES,
        "prompts": ("Name: ", "Wie heißt du? ", "Gib deinen Namen ein: "),
    },
    {
        "type": "int", "variable": "alter", "label": "Alter",
        "values": tuple(range(14, 26)),
        "prompts": ("Alter: ", "Wie alt bist du? ", "Gib dein Alter ein: "),
    },
    {
        "type": "string", "variable": "wohnort", "label": "Wohnort",
        "values": ("Berlin", "München", "Hamburg", "Köln", "Dresden"),
        "prompts": ("Wohnort: ", "Wo wohnst du? ", "Gib deinen Wohnort ein: "),
    },
    {
        "type": "double", "variable": "groesse", "label": "Größe",
        "values": (1.62, 1.68, 1.72, 1.75, 1.80, 1.84, 1.90),
        "prompts": ("Größe: ", "Wie groß bist du? ", "Gib deine Größe in Metern ein: "),
    },
    {
        "type": "int", "variable": "geschwister", "label": "Geschwister",
        "values": (0, 1, 2, 3, 4),
        "prompts": ("Geschwister: ", "Wie viele Geschwister hast du? ",
                    "Gib die Anzahl deiner Geschwister ein: "),
    },
    {
        "type": "string", "variable": "lieblingsfarbe", "label": "Lieblingsfarbe",
        "values": COLORS,
        "prompts": ("Lieblingsfarbe: ", "Was ist deine Lieblingsfarbe? ",
                    "Gib deine Lieblingsfarbe ein: "),
    },
    {
        "type": "double", "variable": "gewicht", "label": "Gewicht",
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
    for field, conversion in zip(fields, conversions):
        prompt = field["prompt"].replace("\\", "\\\\").replace('"', '\\"')
        lines.extend((
            f'Console.Write("{prompt}");',
            _input_conversion(field, conversion),
        ))

    if output_layout == "combined":
        labels = " | ".join(
            f'{field["label"]}: {{{index}}}'
            for index, field in enumerate(fields)
        )
        values = ", ".join(field["variable"] for field in fields)
        if output_style == "interpolation":
            interpolated = " | ".join(
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
    fields = random.sample(INPUT_FIELDS, random.randint(1, 3))
    for field in fields:
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
        f'{field["prompt"].rstrip()}{_input_display_value(field)}'
        for field in fields
    )
    result_lines = [
        f'{field["label"]}: {_input_display_value(field)}'
        for field in fields
    ]
    expected_output = f"{input_output}\n\n" + "\n".join(result_lines)

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

    variable_summary = ", ".join(
        f'{field["type"]} {field["variable"]}' for field in fields
    )
    hints = (
        "Verwende Console.Write() für die Eingabeaufforderungen, "
        "Console.ReadLine() zum Einlesen und die angegebenen Datentypen. "
        "Für int und double sind die beiden üblichen Konvertierungen erlaubt."
    )
    return _program(
        question + f"\nVariablen: {variable_summary}",
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
    body = (
        f'string name = "{name}";\n'
        f"int alter = {age};\n"
        f"double groesse = {height:.2f};\n"
        "Console.WriteLine(name);\n"
        "Console.WriteLine(alter);\n"
        "Console.WriteLine(groesse);\n"
        "Console.ReadLine();"
    )
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
    body = (
        f'string vorname = "{first}";\n'
        f'string nachname = "{last}";\n'
        f"int alter = {age};\n"
        'Console.WriteLine("Name:\\t" + vorname + " " + nachname + '
        '"\\nAlter:\\t" + alter);\n'
        "Console.ReadLine();"
    )
    output = f"Name:\t{first} {last}\nAlter:\t{age}"
    return _program(
        "Erstelle vorname, nachname und alter. Formatiere die Ausgabe mit \\t und "
        "\\n. Verwende dafür genau eine Console.WriteLine-Anweisung.",
        body, output,
        "\\t erzeugt einen Tabulator, \\n einen Zeilenumbruch. Nur eine WriteLine verwenden."
    )


def _operators():
    a, b = _number_pair()
    if random.choice((True, False)):
        total, difference, product = a + b, a - b, a * b
        body = (
            f"int zahl1 = {a};\nint zahl2 = {b};\n"
            "int summe = zahl1 + zahl2;\n"
            "int differenz = zahl1 - zahl2;\n"
            "int produkt = zahl1 * zahl2;\n"
            'Console.WriteLine("Zahl1 = " + zahl1);\n'
            'Console.WriteLine("Zahl2 = " + zahl2);\n'
            'Console.WriteLine("Summe = " + summe);\n'
            'Console.WriteLine("Differenz = " + differenz);\n'
            'Console.WriteLine("Produkt = " + produkt);\n'
            "Console.ReadLine();"
        )
        output = (
            f"Zahl1 = {a}\nZahl2 = {b}\nSumme = {total}\n"
            f"Differenz = {difference}\nProdukt = {product}"
        )
        prompt = (
            "Erstelle zahl1 und zahl2. Berechne Summe, Differenz und Produkt in "
            "eigenen Variablen und gib alle fünf Werte mit Beschriftung aus."
        )
    else:
        body = (
            f"int zahl1 = {a};\nint zahl2 = {b};\n"
            f'Console.WriteLine("{a} == {b}: " + (zahl1 == zahl2));\n'
            f'Console.WriteLine("{a} != {b}: " + (zahl1 != zahl2));\n'
            f'Console.WriteLine("{a} > {b}: " + (zahl1 > zahl2));\n'
            f'Console.WriteLine("{a} < {b}: " + (zahl1 < zahl2));\n'
            "Console.ReadLine();"
        )
        output = (
            f"{a} == {b}: {str(a == b)}\n{a} != {b}: {str(a != b)}\n"
            f"{a} > {b}: {str(a > b)}\n{a} < {b}: {str(a < b)}"
        )
        prompt = (
            "Erstelle zahl1 und zahl2. Vergleiche sie mit ==, !=, > und <. "
            "Gib jeweils den Vergleich und sein Ergebnis aus."
        )
    return _program(prompt, body, output, "Verwende +, -, * sowie ==, !=, > und <.")


def _if_condition():
    age = random.randint(18, 30)
    return _main(
        f"Ergänze nur die Bedingung. Bei einem Alter ab 18 soll 'Volljaehrig' "
        f"ausgegeben werden. Variable: alter = {age}.",
        "",
        __import__("json").dumps({"solution": "alter >= 18", "output": "Volljaehrig" if age >= 18 else ""}, ensure_ascii=False),
        "Vergleiche alter mit 18.",
        question_type="csharp_practice"
    ) | {
        "question_text": (
            f"Ergänze nur die Bedingung. Bei einem Alter ab 18 soll 'Volljaehrig' "
            f"ausgegeben werden. Variable: alter = {age}.\n"
            "static void Main(string[] args)\n{\n"
            f"    int alter = {age};\n"
            "    if (________________)\n    {\n"
            '        Console.WriteLine("Volljaehrig");\n    }\n'
            "    Console.ReadLine();\n}"
        ),
    }


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
    return {
        "subject_name": "AE", "topic_name": None,
        "question_text": (
            "Ergänze nur die Bedingung. Bei mindestens 20 Grad soll 'Warm', "
            f"andernfalls 'Kalt' ausgegeben werden. temperatur = {temperature}.\n"
            "static void Main(string[] args)\n{\n"
            f"    int temperatur = {temperature};\n"
            "    if (________________)\n    {\n"
            '        Console.WriteLine("Warm");\n    }\n    else\n    {\n'
            '        Console.WriteLine("Kalt");\n    }\n'
            "    Console.ReadLine();\n}"
        ),
        "answer": __import__("json").dumps({"solution": "temperatur >= 20", "output": "Warm" if temperature >= 20 else "Kalt"}, ensure_ascii=False),
        "hint": "Vergleiche temperatur mit 20.",
        "difficulty": 1, "question_type": "csharp_practice",
    }


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



GENERATORS = {
    "Ausgabe": _output,
    "Eingabe": _input,
    "Variablen": _variables,
    "Ausgabe formatierung": _formatting,
    "Operatoren": _operators,
    "Bedingungen": random.choice,
    "Verzweigte Bedingungen": random.choice,
}


class CSharpQuestionGenerator:
    """Creates unlimited parameterized exercises for the existing AE/OOP topics."""

    def __init__(self, repository: QuestionRepository):
        self.repository = repository

    def generate_question_id(self, topic_name):
        if topic_name == "Bedingungen":
            question = random.choice((_if_condition, _if_output))()
        elif topic_name == "Verzweigte Bedingungen":
            question = random.choice((_if_else_condition, _if_else_output))()
        else:
            question = GENERATORS[topic_name]()
        question["topic_name"] = topic_name
        return self.repository.add_question(**question)
