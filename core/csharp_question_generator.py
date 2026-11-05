"""Generate fresh, bounded and internally consistent C# practice exercises.

This module generates one new exercise whenever an AE/OOP topic is opened.
It does not execute C#; code submissions are checked against the generated
reference solution, while output-reading tasks use the normal answer field.
"""
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


def _input():
    if random.choice(("name", "age")) == "name":
        name = random.choice(NAMES)
        body = (
            'string name = Console.ReadLine();\n'
            'Console.WriteLine("Name: " + name);\n'
            'Console.WriteLine("Hallo " + name);\n'
            "Console.ReadLine();"
        )
        return _program(
            "Lies einen Namen ein. Gib danach den Namen mit 'Name:' und "
            "anschließend eine Begrüßung mit 'Hallo' aus.\n"
            f"Eingabe: {name}\nVariable: name (string)",
            body, f"Name: {name}\nHallo {name}",
            "Verwende Console.ReadLine(), um den Namen einzulesen.",
            alternatives=(
                'string name = Console.ReadLine();\n'
                'Console.WriteLine($"Name: {name}");\n'
                'Console.WriteLine($"Hallo {name}");\n'
                'Console.ReadLine();',
                'string name = Console.ReadLine();\n'
                'Console.WriteLine("Name: {0}", name);\n'
                'Console.WriteLine("Hallo {0}", name);\n'
                'Console.ReadLine();',
            ),
        )

    age = random.randint(14, 25)
    body = (
        "int age = Convert.ToInt32(Console.ReadLine());\n"
        'Console.WriteLine("Alter: " + age);\n'
        'Console.WriteLine("Du bist " + age + " Jahre alt.");\n'
        "Console.ReadLine();"
    )
    alternatives = (
        "int age = Int32.Parse(Console.ReadLine());\n"
        'Console.WriteLine("Alter: " + age);\n'
        'Console.WriteLine("Du bist " + age + " Jahre alt.");\n'
        "Console.ReadLine();",
    )
    return _program(
        "Lies das Alter als ganze Zahl ein. Gib danach das Alter mit 'Alter:' "
        "und einen Satz mit dem Alter aus.\n"
        f"Eingabe: {age}\nVariable: age (int)",
        body, f"Alter: {age}\nDu bist {age} Jahre alt.",
        "Verwende Console.ReadLine() und wandle die Eingabe mit "
        "Convert.ToInt32() oder Int32.Parse() in int um.",
        alternatives=alternatives,
    )


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
