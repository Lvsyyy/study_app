import json
import random
import re

from core import csharp_question_generator as generator


def _solution(question):
    return json.loads(question["answer"])["solution"]


def test_variable_output_uses_only_one_supported_format():
    for seed in range(30):
        random.seed(seed)
        code = _solution(generator._variables())
        output_lines = [
            line for line in code.splitlines()
            if line.strip().startswith("Console.WriteLine(")
        ]
        assert len(output_lines) == 3
        assert all(
            re.search(r'Console\.WriteLine\(\$"\{(?:name|alter|groesse)\}"\);', line)
            or re.search(r'Console\.WriteLine\("\{0\}", (?:name|alter|groesse)\);', line)
            for line in output_lines
        )


def test_formatting_output_uses_interpolation_or_composite_formatting():
    for seed in range(30):
        random.seed(seed)
        code = _solution(generator._formatting())
        assert "+" not in next(
            line for line in code.splitlines()
            if line.strip().startswith("Console.WriteLine(")
        )
        assert (
            'Console.WriteLine($"Name:' in code
            or 'Console.WriteLine("Name:' in code
        )


def test_operator_output_uses_selected_format_for_each_variable_line():
    for seed in range(60):
        random.seed(seed)
        code = _solution(generator._operators())
        output_lines = [
            line for line in code.splitlines()
            if line.strip().startswith("Console.WriteLine(")
        ]
        assert output_lines
        assert all(
            line.startswith('Console.WriteLine($"')
            or re.search(r'^Console\.WriteLine\(".*", .+\);$', line)
            for line in output_lines
        )
        assert not any(' + "' in line or '" + ' in line for line in output_lines)
