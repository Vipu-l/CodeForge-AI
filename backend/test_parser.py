from app.services.code_parser import parse_python_file


chunks = parse_python_file("app/main.py")


for chunk in chunks:
    print("\n--------------------")
    print("Type:", chunk["type"])
    print("Name:", chunk["name"])
    print("Lines:", chunk["start_line"], "-", chunk["end_line"])
    print("Code:")
    print(chunk["code"])