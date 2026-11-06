import json

from ui import question_content as content


def question(answer, question_type="text", subject="BS", text="Frage?"):
    return {
        "answer": answer if isinstance(answer, str) else json.dumps(answer),
        "question_type": question_type,
        "subject_name": subject,
        "question_text": text,
    }


def test_modes_follow_the_original_dispatch_order():
    assert content.question_mode("pap", "BS", "x") == content.PAP
    assert content.question_mode("code", "BS", "x") == content.CODE
    assert content.question_mode("batch", "BS", "x") == content.BATCH
    assert content.question_mode("csharp_practice", "AE", "x") == content.CSHARP
    assert content.question_mode("multi_select", "BS", "x") == content.INTERACTIVE
    assert content.question_mode("text", "BS", "x") == content.TEXT


def test_ae_code_like_text_uses_the_code_view_and_plain_text_does_not():
    body = "static void Main()\n{\n    Console.WriteLine(1);\n}"
    assert content.question_mode("text", "AE", body) == content.CODE
    assert content.question_mode("text", "AE", "Was ist ein Algorithmus?") == content.TEXT
    assert content.question_mode("text", "BS", body) == content.TEXT


def test_table_template_selects_the_table_view():
    template = {"headers": ["Rechnung", "R", "GQ"], "rows": [["", "", ""]]}
    assert content.question_mode("text", "AE", "x", template) == content.TABLE
    multi = {"tables": [{**template, "title": "Teil 1"}]}
    assert content.question_mode("text", "AE", "x", multi) == content.TABLE


def test_has_tables_accepts_single_and_multi_table_shapes():
    assert content.has_tables({"headers": ["a"], "rows": [["1"]]})
    assert content.has_tables({"tables": []})
    assert not content.has_tables({"solution": "print(1)"})
    assert not content.has_tables(None)


def test_split_code_question_separates_shell_from_body():
    text = (
        "Schreibe ein Programm.\n"
        "using System;\n"
        "class Program\n"
        "{\n"
        "    static void Main()\n"
        "    {\n"
        "        int x = 1;\n"
        "        Console.WriteLine(x);\n"
        "    }\n"
        "}"
    )
    prompt, prefix, body, suffix = content.split_code_question(text)
    assert prompt == "Schreibe ein Programm.\nusing System;\nclass Program\n{"
    assert prefix == "static void Main()\n{"
    assert body.strip() == "int x = 1;\n        Console.WriteLine(x);"
    assert suffix == "}"


def test_split_code_question_without_main_returns_the_prompt():
    prompt, prefix, body, suffix = content.split_code_question("Nur Text")
    assert (prompt, prefix, body, suffix) == ("Nur Text", "", "", "")


def test_condition_matching_ignores_whitespace():
    entered = "if (alter >= 18)\n{\n}"
    assert content.condition_answer_matches(entered, "alter>=18")
    assert not content.condition_answer_matches(entered, "alter>18")
    assert not content.condition_answer_matches("kein if", "alter>=18")


def test_code_matching_ignores_indentation_and_accepts_alternatives():
    entered = "int x = 1;\nConsole.WriteLine(x);"
    expected = "\n".join(("    int x = 1;", "    Console.WriteLine(x);"))
    assert content.code_answer_matches(entered, expected)
    assert content.code_answer_matches(entered, expected, ("anderes;",))
    assert not content.code_answer_matches("", expected)


def test_console_comparison_ignores_trailing_whitespace_and_blank_lines():
    assert content.normalize_console("a  \r\n\r\nb\n\n") == "a\n\nb"
    assert content.compact("a  >=  1") == "a>=1"


def test_pap_solution_lists_blocks_and_connections():
    data = {
        "nodes": [
            {"id": "n1", "type": "Start", "text": "Start"},
            {"id": "n2", "type": "Ausgabe", "text": "Hallo"},
        ],
        "edges": [{"from": "n1", "to": "n2", "label": "Normal"}],
    }
    text = content.format_solution_text(question(data, "pap"), data, content.PAP)
    assert "Flowchart blocks:" in text
    assert "- Start: Start" in text and "- Ausgabe: Hallo" in text
    assert "Connections:" in text
    assert "Start --[Normal]--> Hallo" in text


def test_interactive_solutions_cover_every_kind():
    multi = {"options": ["a", "b", "c"], "correct": [0, 2]}
    text = content.format_solution_text(
        question(multi, "multi_select"), multi, content.INTERACTIVE, "multi_select"
    )
    assert "Correct options:" in text and "✓ a" in text and "✓ c" in text

    ordering = {"items": ["eins", "zwei"]}
    text = content.format_solution_text(
        question(ordering, "ordering"), ordering, content.INTERACTIVE, "ordering"
    )
    assert "1. eins" in text and "2. zwei" in text

    matching = {"pairs": [{"left": "A", "right": "B"}]}
    text = content.format_solution_text(
        question(matching, "matching"), matching, content.INTERACTIVE, "matching"
    )
    assert "A  →  B" in text

    table_sort = {
        "categories": ["Hardware"],
        "cards": [{"text": "CPU", "category": "Hardware"}],
    }
    text = content.format_solution_text(
        question(table_sort, "table_sort"), table_sort, content.INTERACTIVE, "table_sort"
    )
    assert "Hardware: CPU" in text


def test_batch_and_csharp_solutions_include_their_output():
    batch = {"solution": "SET /A 4*5", "expected_output": ["20"]}
    text = content.format_solution_text(question(batch, "batch"), batch, content.BATCH)
    assert "SET /A 4*5" in text and "20" in text

    csharp = {"solution": "int x = 1;", "output": "1"}
    text = content.format_solution_text(
        question(csharp, "csharp_practice"), csharp, content.CSHARP
    )
    assert "int x = 1;" in text and "Console output:" in text


def test_plain_and_code_solutions_fall_back_gracefully():
    assert content.format_solution_text(question("42"), None, content.TEXT) == "42"
    assert content.format_solution_text(question("42", "code"), None, content.CODE).strip() == "42"
    assert content.parse_answer("not json") is None
    assert content.parse_answer('{"a": 1}') == {"a": 1}
