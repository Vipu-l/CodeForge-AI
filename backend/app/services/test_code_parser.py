from app.services.code_parser import parse_python_file


def test_parse_python_file():

    chunks = parse_python_file(
        "app/main.py"
    )

    assert isinstance(chunks, list)

    assert any(
        chunk["type"] == "function"
        for chunk in chunks
    )